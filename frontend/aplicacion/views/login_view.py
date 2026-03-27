from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class LoginView(QFrame):
    login_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginFrame")

        wrapper = QHBoxLayout(self)
        wrapper.setContentsMargins(36, 36, 36, 36)
        wrapper.addStretch(1)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setMaximumWidth(440)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(18)

        brand = QLabel("VaultDesk")
        brand.setObjectName("BrandTitle")
        subtitle = QLabel("Acceso seguro al entorno administrativo")
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña maestra")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._emit_login)

        login_button = QPushButton("Acceder")
        login_button.setObjectName("PrimaryButton")
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.clicked.connect(self._emit_login)

        self.status_label = QLabel("Sesion protegida. El acceso se valida contra backend.")
        self.status_label.setObjectName("MutedText")
        self.status_label.setWordWrap(True)

        layout.addWidget(brand)
        layout.addWidget(subtitle)
        layout.addSpacing(6)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(self.status_label)

        wrapper.addWidget(card, alignment=Qt.AlignCenter)
        wrapper.addStretch(1)

    def _emit_login(self):
        self.login_requested.emit(self.password_input.text())

    def set_status(self, message: str, is_error: bool = False):
        color = "#f28b82" if is_error else "#8b98a7"
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setText(message)
