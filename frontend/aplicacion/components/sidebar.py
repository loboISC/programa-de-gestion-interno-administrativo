from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QPushButton, QVBoxLayout


class Sidebar(QFrame):
    section_selected = Signal(str)

    def __init__(self, sections: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(250)
        self.sections = sections

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 20, 18, 20)
        layout.setSpacing(14)

        title = QLabel("VaultDesk")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("Administracion segura")
        subtitle.setObjectName("SidebarCaption")

        layout.addWidget(title)
        layout.addWidget(subtitle)
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
