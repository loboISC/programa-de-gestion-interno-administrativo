APP_STYLESHEET = """
QWidget {
    background-color: #11161d;
    color: #e6edf3;
    font-family: "DejaVu Sans";
    font-size: 13px;
}

QMainWindow, QFrame#RootFrame, QFrame#ShellFrame, QFrame#LoginFrame {
    background-color: #11161d;
}

QFrame#Sidebar {
    background-color: #171d25;
    border: 1px solid #242c36;
    border-radius: 24px;
}

QFrame#ContentPanel, QFrame#SurfaceCard, QFrame#HeaderCard {
    background-color: #171d25;
    border: 1px solid #242c36;
    border-radius: 22px;
}

QFrame#LoginCard {
    background-color: #171d25;
    border: 1px solid #293240;
    border-radius: 28px;
}

QLabel#BrandTitle {
    font-size: 26px;
    font-weight: 700;
    color: #f8fbff;
}

QLabel#SectionTitle {
    font-size: 22px;
    font-weight: 700;
    color: #f8fbff;
}

QLabel#MutedText, QLabel#SidebarCaption {
    color: #8b98a7;
}

QLabel#MetricValue {
    font-size: 30px;
    font-weight: 700;
    color: #f4f8fb;
}

QLabel#MetricLabel {
    color: #8b98a7;
    font-size: 12px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QPushButton {
    background-color: #222b36;
    border: 1px solid #313c49;
    border-radius: 14px;
    padding: 10px 14px;
}

QPushButton:hover {
    background-color: #293443;
}

QPushButton:pressed {
    background-color: #313e4e;
}

QPushButton#PrimaryButton {
    background-color: #2f7df4;
    border: 1px solid #3d89ff;
    color: white;
    font-weight: 600;
}

QPushButton#PrimaryButton:hover {
    background-color: #3b88fd;
}

QPushButton#DangerButton {
    background-color: #3a2226;
    border: 1px solid #6a343d;
}

QPushButton#SidebarButton {
    text-align: left;
    padding: 12px 14px;
    border-radius: 16px;
    background-color: transparent;
    border: 1px solid transparent;
    font-weight: 600;
}

QPushButton#SidebarButton:hover {
    background-color: #212a35;
    border-color: #2f3946;
}

QPushButton#SidebarButton:checked {
    background-color: #24354f;
    border-color: #3f78c7;
    color: #f8fbff;
}

QLineEdit, QPlainTextEdit, QComboBox, QDateEdit {
    background-color: #0f141b;
    border: 1px solid #2c3744;
    border-radius: 14px;
    padding: 10px 12px;
    selection-background-color: #2f7df4;
}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #3d89ff;
}

QTableWidget {
    background-color: #11161d;
    border: 1px solid #293240;
    border-radius: 16px;
    gridline-color: #1d2530;
}

QHeaderView::section {
    background-color: #171d25;
    color: #9ba7b5;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #293240;
    font-weight: 600;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #1d2530;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 6px 0 6px 0;
}

QScrollBar::handle:vertical {
    background: #344152;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical,
QScrollBar:horizontal {
    background: transparent;
    border: none;
}
"""
