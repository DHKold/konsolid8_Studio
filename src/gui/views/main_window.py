from PySide6.QtWidgets import QMainWindow, QStatusBar, QToolBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Konsolid8 Studio")
        self.setGeometry(100, 100, 800, 600)

        # Add toolbar and status bar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
