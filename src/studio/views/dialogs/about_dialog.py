from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Konsolid8 Studio")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Konsolid8 Studio v0.1.0"))
        layout.addWidget(QLabel("Developed by Cedric van Eetvelde"))
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        self.setLayout(layout)
