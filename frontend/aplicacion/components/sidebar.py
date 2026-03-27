from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class Sidebar(QFrame):
    section_selected = Signal(str)

    def __init__(self, sections: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(250)
        self.sections = sections

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 22, 18, 20)
        layout.setSpacing(14)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)

        logo_label = QLabel()
        logo_label.setObjectName("LogoMark")
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "logoprincipal.png"
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo_label.setPixmap(
                pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        brand_text = QVBoxLayout()
        title = QLabel("VaultDesk")
        title.setObjectName("SidebarBrandTitle")
        subtitle = QLabel("Administracion segura")
        subtitle.setObjectName("SidebarCaption")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)

        brand_row.addWidget(logo_label, alignment=Qt.AlignTop)
        brand_row.addLayout(brand_text)

        layout.addLayout(brand_row)
        layout.addSpacing(10)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for key, label in sections:
            button = QPushButton(label)
            button.setObjectName("SidebarButton")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setProperty("section_key", key)
            button.clicked.connect(lambda checked=False, section=key: self.section_selected.emit(section))
            self.button_group.addButton(button)
            layout.addWidget(button)

        layout.addStretch(1)
