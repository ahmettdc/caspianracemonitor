import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QWidget, QFormLayout
)
from PyQt6.QtCore import Qt

DATA_DIR = "data/teams_drivers"

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Takım Ayarları")
        self.setMinimumWidth(400)

        os.makedirs(DATA_DIR, exist_ok=True)
        self.teams_data = self.load_all_teams()

        self.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 0.4);
                padding: 4px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #ffd700;
                color: black;
                font-size: 14px;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #ffcc00;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
        """)

        layout = QVBoxLayout(self)

        # Dropdown ile mevcut takımlar listelenir
        self.team_selector = QComboBox()
        self.team_selector.addItem("--- Yeni Takım ---")
        self.team_selector.addItems(sorted(self.teams_data.keys()))
        self.team_selector.currentTextChanged.connect(self.populate_fields)
        layout.addWidget(QLabel("Takım Seç:"))
        layout.addWidget(self.team_selector)

        # Yeni takım adı girilecek alan
        self.team_input = QLineEdit()
        layout.addWidget(QLabel("Takım İsmi:"))
        layout.addWidget(self.team_input)

        # 6 adet pilot alanı
        self.driver_inputs = []
        form_layout = QFormLayout()
        for i in range(6):
            inp = QLineEdit()
            form_layout.addRow(f"Pilot {i + 1}:", inp)
            self.driver_inputs.append(inp)
        layout.addLayout(form_layout)

        # Kaydet butonu
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_team)
        layout.addWidget(self.save_button)

    def load_all_teams(self):
        teams = {}
        if os.path.exists(DATA_DIR):
            for file in os.listdir(DATA_DIR):
                if file.endswith(".json"):
                    team_name = file.replace(".json", "")
                    try:
                        with open(os.path.join(DATA_DIR, file), "r", encoding="utf-8") as f:
                            data = json.load(f)
                            teams[team_name] = data
                    except Exception as e:
                        print(f"Hata ({file}):", e)
        return teams

    def populate_fields(self, team_name):
        if team_name != "--- Yeni Takım ---" and team_name in self.teams_data:
            self.team_input.setText(team_name)
            drivers = self.teams_data[team_name].get("drivers", [])
            for i, input_field in enumerate(self.driver_inputs):
                input_field.setText(drivers[i] if i < len(drivers) else "")
        else:
            self.team_input.clear()
            for input_field in self.driver_inputs:
                input_field.clear()

    def save_team(self):
        team_name = self.team_input.text().strip()
        drivers = [i.text().strip() for i in self.driver_inputs]
        non_empty = [d for d in drivers if d]

        if not team_name:
            QMessageBox.warning(self, "Hata", "Takım ismi boş olamaz.")
            return
        if not non_empty:
            QMessageBox.warning(self, "Hata", "En az bir pilot ismi girilmelidir.")
            return

        filepath = os.path.join(DATA_DIR, f"{team_name}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"drivers": drivers}, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Başarılı", f"{team_name} takımı kaydedildi.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt hatası:\n{e}")
