from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class PlaceholderView(QFrame):
    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        description_label = QLabel(description)
        description_label.setObjectName("MutedText")
        description_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch(1)
