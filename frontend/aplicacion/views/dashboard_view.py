from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout

from components.cards import SummaryCard
from views.login_view import RegisterUserDialog


class DashboardView(QFrame):
    register_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        header = QLabel("Dashboard")
        header.setObjectName("SectionTitle")
        helper = QLabel("Resumen rapido de credenciales, proveedores y actividad reciente.")
        helper.setObjectName("MutedText")

        cards_grid = QGridLayout()
        cards_grid.setHorizontalSpacing(16)
        cards_grid.setVerticalSpacing(16)
        cards_grid.addWidget(SummaryCard("Credenciales guardadas", "24"), 0, 0)
        cards_grid.addWidget(SummaryCard("Proveedores activos", "7"), 0, 1)
        cards_grid.addWidget(SummaryCard("Ultimos accesos", "5 hoy"), 0, 2)

        quick_actions = QFrame()
        quick_actions.setObjectName("SurfaceCard")
        actions_layout = QVBoxLayout(quick_actions)
        actions_layout.setContentsMargins(20, 20, 20, 20)
        actions_layout.setSpacing(12)
        actions_layout.addWidget(QLabel("Accesos rapidos"))
        add_credential_button = QPushButton("Agregar credencial")
        add_credential_button.setObjectName("PrimaryButton")
        add_credential_button.clicked.connect(self.open_register_dialog)
        actions_layout.addWidget(add_credential_button)
        actions_layout.addWidget(QPushButton("Registrar proveedor"))
        actions_layout.addWidget(QPushButton("Subir documento"))

        layout.addWidget(header)
        layout.addWidget(helper)
        layout.addLayout(cards_grid)
        layout.addWidget(quick_actions)
        layout.addStretch(1)

    def open_register_dialog(self) -> None:
        dialog = RegisterUserDialog(self)
        if dialog.exec():
            self.register_requested.emit(dialog.get_payload())
