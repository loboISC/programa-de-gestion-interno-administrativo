from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class RegisterUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear credenciales")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")

        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Nombre completo")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo opcional")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.hint_input = QLineEdit()
        self.hint_input.setPlaceholderText("Pista opcional")

        form.addRow("Usuario", self.username_input)
        form.addRow("Nombre", self.full_name_input)
        form.addRow("Correo", self.email_input)
        form.addRow("Contraseña", self.password_input)
        form.addRow("Confirmar", self.confirm_password_input)
        form.addRow("Pista", self.hint_input)

        self.status_label = QLabel("Crea las credenciales con las que después entrarás al sistema.")
        self.status_label.setObjectName("MutedText")
        self.status_label.setWordWrap(True)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Crear usuario")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self._validate_and_accept)
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        layout.addLayout(form)
        layout.addWidget(self.status_label)
        layout.addLayout(buttons)

    def _validate_and_accept(self):
        if self.password_input.text() != self.confirm_password_input.text():
            self.status_label.setStyleSheet("color: #b24d3e;")
            self.status_label.setText("Las contraseñas no coinciden.")
            return
        if not self.username_input.text().strip() or not self.full_name_input.text().strip() or not self.password_input.text():
            self.status_label.setStyleSheet("color: #b24d3e;")
            self.status_label.setText("Usuario, nombre y contraseña son obligatorios.")
            return
        self.accept()

    def get_payload(self) -> dict:
        return {
            "username": self.username_input.text().strip(),
            "full_name": self.full_name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "password": self.password_input.text(),
            "password_hint": self.hint_input.text().strip(),
        }


class LoginView(QFrame):
    login_requested = Signal(str, str)
    register_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginFrame")

        wrapper = QHBoxLayout(self)
        wrapper.setContentsMargins(36, 36, 36, 36)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setMaximumWidth(980)

        main_layout = QHBoxLayout(card)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        showcase = QFrame()
        showcase.setObjectName("LoginShowcase")
        showcase_layout = QVBoxLayout(showcase)
        showcase_layout.setContentsMargins(30, 30, 30, 30)
        showcase_layout.setSpacing(16)

        logo_label = QLabel()
        logo_label.setObjectName("LogoMark")
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "logoprincipal.png"
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo_label.setPixmap(
                pixmap.scaled(300, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_label.setAlignment(Qt.AlignCenter)

        showcase_title = QLabel("Seguridad y control en un solo escritorio")
        showcase_title.setObjectName("SectionTitle")
        showcase_title.setWordWrap(True)
        showcase_text = QLabel(
            "Ssitema de gestion ."
        )
        showcase_text.setObjectName("MutedText")
        showcase_text.setWordWrap(True)

        showcase_layout.addWidget(logo_label)
        showcase_layout.addWidget(showcase_title)
        showcase_layout.addWidget(showcase_text)
        showcase_layout.addStretch(1)

        form_frame = QFrame()
        form_frame.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(form_frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        brand = QLabel("SGA ")
        brand.setObjectName("BrandTitle")
        subtitle = QLabel("Acceso seguro")
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.returnPressed.connect(self._emit_login)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._emit_login)

        login_button = QPushButton("Acceder")
        login_button.setObjectName("PrimaryButton")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self._emit_login)

        register_button = QPushButton("Crear credenciales")
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.clicked.connect(self._open_register_dialog)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addWidget(register_button)
        buttons.addWidget(login_button)

        self.status_label = QLabel("Sesion protegida. El acceso se valida contra backend.")
        self.status_label.setObjectName("MutedText")
        self.status_label.setWordWrap(True)

        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addSpacing(6)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addLayout(buttons)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        main_layout.addWidget(showcase, 6)
        main_layout.addWidget(form_frame, 4)

        wrapper.addStretch(1)
        wrapper.addWidget(card, alignment=Qt.AlignCenter)
        wrapper.addStretch(1)

    def _emit_login(self):
        self.login_requested.emit(self.username_input.text().strip(), self.password_input.text())

    def _open_register_dialog(self):
        dialog = RegisterUserDialog(self)
        if dialog.exec():
            self.register_requested.emit(dialog.get_payload())

    def fill_credentials(self, username: str, password: str) -> None:
        self.username_input.setText(username)
        self.password_input.setText(password)

    def set_status(self, message: str, is_error: bool = False):
        color = "#b24d3e" if is_error else "#7c7368"
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setText(message)
