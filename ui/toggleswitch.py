from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt

class ToggleSwitch(QWidget):
    def __init__(self, label_text="Toggle View", initial=True, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)  # biraz boşluk bırak
        layout.setSpacing(10)  # yazı ile switch arası

        self.label = QLabel(label_text)
        self.label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("RealToggleSwitch")
        self.checkbox.setChecked(initial)

        self.checkbox.setStyleSheet("""
        QCheckBox::indicator {
            width: 50px;
            height: 26px;
            border-radius: 13px;
            background-color: #555;
            border: 2px solid #aaa;
        }
        QCheckBox::indicator:checked {
            background-color: #FFD700;
            border: 2px solid #FFD700;
        }
        QCheckBox::indicator:unchecked {
            background-color: #555;
            border: 2px solid #aaa;
        }
        """)

        layout.addWidget(self.label)
        layout.addWidget(self.checkbox)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setChecked(self, checked):
        self.checkbox.setChecked(checked)

    def stateChanged(self):
        return self.checkbox.stateChanged
