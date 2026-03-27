import sys

from PySide6.QtWidgets import QApplication

from views.main_window import AdminSystemApp


def run() -> int:
    app = QApplication(sys.argv)
    window = AdminSystemApp()
    window.show()
    return app.exec()

