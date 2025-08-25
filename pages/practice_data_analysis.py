from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class PracticeDataAnalysis(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Welcome to Practice Data Analysis Page!")
        layout.addWidget(label)
        self.setLayout(layout)
