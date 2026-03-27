APP_STYLESHEET = """
QWidget {
    background-color: #f5f1e8;
    color: #2c2a28;
    font-family: "DejaVu Sans";
    font-size: 13px;
}

QMainWindow, QFrame#RootFrame, QFrame#ShellFrame, QFrame#LoginFrame {
    background-color: #f5f1e8;
}

QFrame#Sidebar {
    background-color: #f8f4ec;
    border: 1px solid #ddd2c1;
    border-radius: 28px;
}

QFrame#ContentPanel, QFrame#SurfaceCard, QFrame#HeaderCard {
    background-color: #fffdfa;
    border: 1px solid #e3d8c8;
    border-radius: 24px;
}

QFrame#LoginCard {
    background-color: #fffdfa;
    border: 1px solid #ded2c3;
    border-radius: 32px;
}

QFrame#LoginShowcase {
    background-color: #ece4d8;
    border: 1px solid #dfd2c1;
    border-radius: 26px;
}

QLabel#LogoMark {
    background: transparent;
}

QLabel#SidebarBrandTitle {
    font-size: 18px;
    font-weight: 700;
    color: #272421;
}

QLabel#BrandTitle {
    font-size: 28px;
    font-weight: 700;
    color: #23201d;
}

QLabel#SectionTitle {
    font-size: 22px;
    font-weight: 700;
    color: #23201d;
}

QLabel#MutedText, QLabel#SidebarCaption {
    color: #7c7368;
}

QLabel#MetricValue {
    font-size: 30px;
    font-weight: 700;
    color: #23201d;
}

QLabel#MetricLabel {
    color: #8b7f71;
    font-size: 12px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QPushButton {
    background-color: #f3ece2;
    border: 1px solid #d9ccb9;
    border-radius: 14px;
    padding: 10px 14px;
}

QPushButton:hover {
    background-color: #ece2d5;
}

QPushButton:pressed {
    background-color: #e4d8ca;
}

QPushButton#PrimaryButton {
    background-color: #2f3438;
    border: 1px solid #3b4348;
    color: #fbf8f4;
    font-weight: 600;
}

QPushButton#PrimaryButton:hover {
    background-color: #3d4449;
}

QPushButton#DangerButton {
    background-color: #fbe7e4;
    border: 1px solid #d7aaa3;
    color: #7d3025;
}

QPushButton#SidebarButton {
    text-align: left;
    padding: 13px 15px;
    border-radius: 18px;
    background-color: transparent;
    border: 1px solid transparent;
    font-weight: 600;
}

QPushButton#SidebarButton:hover {
    background-color: #efe6da;
    border-color: #ddcfbd;
}

QPushButton#SidebarButton:checked {
    background-color: #2f3438;
    border-color: #2f3438;
    color: #fcfaf7;
}

QLineEdit, QPlainTextEdit, QComboBox, QDateEdit {
    background-color: #fcfaf7;
    border: 1px solid #d8cab7;
    border-radius: 14px;
    padding: 10px 12px;
    selection-background-color: #b7c5d1;
}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #837560;
}

QTableWidget {
    background-color: #fffdfa;
    border: 1px solid #e2d6c6;
    border-radius: 16px;
    gridline-color: #efe7db;
    alternate-background-color: #faf5ed;
}

QHeaderView::section {
    background-color: #f3ecdf;
    color: #6f665d;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #e0d2c1;
    font-weight: 600;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #efe7db;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 6px 0 6px 0;
}

QScrollBar::handle:vertical {
    background: #cbbda9;
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
