from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class SummaryCard(QFrame):
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("SurfaceCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)

        metric_value = QLabel(value)
        metric_value.setObjectName("MetricValue")
        metric_label = QLabel(label)
        metric_label.setObjectName("MetricLabel")

        layout.addWidget(metric_value)
        layout.addWidget(metric_label)
