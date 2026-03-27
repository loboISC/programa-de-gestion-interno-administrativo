from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout


class HostingProvidersView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Proveedores de Hosting")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Base inicial para CRUD de proveedores y accesos rapidos.")
        subtitle.setObjectName("MutedText")
        add_button = QPushButton("Agregar proveedor")
        add_button.setObjectName("PrimaryButton")

        table = QTableWidget(3, 4)
        table.setHorizontalHeaderLabels(["Proveedor", "URL", "Usuario", "Accion"])
        rows = [
            ("AWS", "https://aws.amazon.com", "admin.aws", "Abrir"),
            ("Hostinger", "https://hpanel.hostinger.com", "ops.host", "Abrir"),
            ("DigitalOcean", "https://cloud.digitalocean.com", "root.ops", "Abrir"),
        ]
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                table.setItem(row_index, col_index, QTableWidgetItem(value))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(add_button)
        layout.addWidget(table)
