import sys

from PySide6.QtWidgets import QApplication

from ..views.main_window import MainWindow


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec())
