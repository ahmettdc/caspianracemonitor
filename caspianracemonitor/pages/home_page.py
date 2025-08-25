# pages/home_page.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Welcome to Home Page!")
        layout.addWidget(label)
        self.setLayout(layout)
