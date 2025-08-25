from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from pages.strategy_form import StrategyForm
from pages.table_component import TableComponent
import os

class PreRaceStintCalculator(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)

        self.strategy_form = StrategyForm()
        self.table_component = TableComponent()

        # ✅ Ana bileşenleri ekle
        scroll_layout.addWidget(self.strategy_form)
        scroll_layout.addWidget(self.table_component)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # ✅ Signal bağlantıları
        self.strategy_form.data_ready.connect(self.table_component.update_table)

        self.strategy_form.save_button.clicked.connect(
            lambda: self.table_component.save_strategy_data(
                os.path.splitext(os.path.basename(self.strategy_form.get_current_filename()))[0]
            )
        )

        self.strategy_form.load_button.clicked.connect(
            lambda: self.table_component.load_strategy_data(
                os.path.splitext(os.path.basename(self.strategy_form.get_current_filename()))[0]
            )
        )
