from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget

from api_client import ApiClient
from components.header import HeaderBar
from components.sidebar import Sidebar
from styles import APP_STYLESHEET
from views.dashboard_view import DashboardView
from views.documentation_view import DocumentationView
from views.hosting_view import HostingProvidersView
from views.login_view import LoginView
from views.password_vault_view import PasswordVaultView
from views.placeholder_view import PlaceholderView


class SessionActivityFilter(QObject):
    def __init__(self, on_activity, parent=None):
        super().__init__(parent)
        self.on_activity = on_activity

    def eventFilter(self, watched, event):
        if event.type() in (
            QEvent.MouseButtonPress,
            QEvent.KeyPress,
            QEvent.FocusIn,
        ):
            self.on_activity()
        return super().eventFilter(watched, event)


class AdminSystemApp(QMainWindow):
    SESSION_TIMEOUT_MS = 10 * 60 * 1000

    def __init__(self):
        super().__init__()
        self.api_client = ApiClient()
        self.current_user = "irvingag"

        self.setWindowTitle("VaultDesk | Sistema Administrativo")
        self.resize(1440, 900)
        self.setStyleSheet(APP_STYLESHEET)

        self.root = QStackedWidget()
        self.setCentralWidget(self.root)

        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.handle_login)

        self.shell_page = self._build_shell_page()

        self.root.addWidget(self.login_view)
        self.root.addWidget(self.shell_page)
        self.root.setCurrentWidget(self.login_view)

        self.session_timer = QTimer(self)
        self.session_timer.setInterval(self.SESSION_TIMEOUT_MS)
        self.session_timer.timeout.connect(self.expire_session)

        self.activity_filter = SessionActivityFilter(self.reset_session_timer, self)
        self.installEventFilter(self.activity_filter)

    def _build_shell_page(self) -> QWidget:
        page = QWidget()
        root_layout = QHBoxLayout(page)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(18)

        sections = [
            ("dashboard", "Dashboard"),
            ("hosting", "Proveedores de Hosting"),
            ("vault", "Password Vault"),
            ("docs", "Documentacion Tecnica"),
            ("notifications", "Notificaciones"),
            ("settings", "Configuracion"),
        ]

        self.sidebar = Sidebar(sections)
        self.sidebar.section_selected.connect(self.navigate_to)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(18)

        self.header = HeaderBar("VaultDesk", self.current_user)
        self.content_stack = QStackedWidget()

        self.views = {
            "dashboard": DashboardView(),
            "hosting": HostingProvidersView(),
            "vault": PasswordVaultView(api_client=self.api_client),
            "docs": DocumentationView(),
            "notifications": PlaceholderView(
                "Notificaciones",
                "Centro de alertas para actividad reciente, vencimientos y recordatorios.",
            ),
            "settings": PlaceholderView(
                "Configuracion",
                "Aqui puedes preparar ajustes de API, cifrado, sesion y preferencias visuales.",
            ),
        }

        for key in sections:
            self.content_stack.addWidget(self.views[key[0]])

        content_layout.addWidget(self.header)
        content_layout.addWidget(self.content_stack, 1)

        root_layout.addWidget(self.sidebar)
        root_layout.addLayout(content_layout, 1)

        self.navigate_to("dashboard")
        return page

    def handle_login(self, master_password: str) -> None:
        if not master_password.strip():
            self.login_view.set_status("Debes ingresar la contraseña maestra.", is_error=True)
            return

        try:
            response = self.api_client.login(master_password)
        except Exception as exc:
            self.login_view.set_status(f"No fue posible iniciar sesión: {exc}", is_error=True)
            return

        self.current_user = response["user"]["username"]
        self.header.set_username(self.current_user)
        self.login_view.password_input.clear()
        self.login_view.set_status("Acceso concedido. Sesion iniciada correctamente.")
        self.root.setCurrentWidget(self.shell_page)
        self.views["vault"].load_credentials()
        self.reset_session_timer()

    def navigate_to(self, section: str) -> None:
        view = self.views.get(section)
        if view is None:
            return
        self.content_stack.setCurrentWidget(view)
        if section == "vault":
            self.views["vault"].load_credentials()
        for button in self.sidebar.button_group.buttons():
            button.setChecked(button.property("section_key") == section)

    def reset_session_timer(self) -> None:
        if self.root.currentWidget() is self.shell_page:
            self.session_timer.start()

    def expire_session(self) -> None:
        self.session_timer.stop()
        self.api_client.set_token(None)
        self.root.setCurrentWidget(self.login_view)
        self.login_view.set_status("La sesion expiro por inactividad. Vuelve a autenticarte.", is_error=True)
        QMessageBox.information(
            self,
            "Sesion finalizada",
            "La sesion fue cerrada por inactividad para proteger tus credenciales.",
        )
