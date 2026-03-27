from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class HeaderBar(QFrame):
    def __init__(self, system_name: str, username: str, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)

        left_column = QVBoxLayout()
        title = QLabel(system_name)
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Panel administrativo personal")
        subtitle.setObjectName("MutedText")
        left_column.addWidget(title)
        left_column.addWidget(subtitle)

        layout.addLayout(left_column)
        layout.addStretch(1)

        user_block = QVBoxLayout()
        self.user_label = QLabel(username)
        self.user_label.setStyleSheet("font-weight: 700; font-size: 15px;")
        role_label = QLabel("Ingeniero en sistemas")
        role_label.setObjectName("MutedText")
        user_block.addWidget(self.user_label)
        user_block.addWidget(role_label)

        layout.addLayout(user_block)

    def set_username(self, username: str) -> None:
        self.user_label.setText(username)
