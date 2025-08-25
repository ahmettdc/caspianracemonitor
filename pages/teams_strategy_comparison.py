from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TeamsStrategyComparison(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Welcome to Teams Strategy Comparison Page!")
        layout.addWidget(label)
        self.setLayout(layout)
