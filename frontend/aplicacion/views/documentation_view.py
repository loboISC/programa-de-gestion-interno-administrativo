from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout


class DocumentationView(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Documentacion Tecnica")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Repositorio interno de notas, PDFs y procedimientos.")
        subtitle.setObjectName("MutedText")
        add_button = QPushButton("Agregar documento")
        add_button.setObjectName("PrimaryButton")

        table = QTableWidget(3, 4)
        table.setHorizontalHeaderLabels(["Titulo", "Descripcion", "Tipo", "Fecha"])
        rows = [
            ("Runbook VPS", "Pasos de hardening", "PDF", "2026-03-10"),
            ("Checklist DNS", "Verificacion de zonas", "TXT", "2026-03-15"),
            ("Notas Flask API", "Integracion backend", "Notas", "2026-03-20"),
        ]
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                table.setItem(row_index, col_index, QTableWidgetItem(value))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(add_button)
        layout.addWidget(table)
