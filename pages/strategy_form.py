from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from pages.strategy_utils import (
    parse_race_time,
    parse_average_lap_time,
    parse_integer,
    parse_float_one_decimal,
    parse_float_two_decimal
)
import os, json

class StrategyForm(QWidget):
    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.inputs = {}

        main_layout = QVBoxLayout(self)

        # Üst başlık
        title_label = QLabel("PreRace Stint Calculator")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            border-bottom: 2px solid #960018;
            padding-bottom: 10px;
            margin-bottom: 20px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Time Section ---
        time_section = self.create_section("⏱ Time Section", [
            ("Race Time (hh:mm:ss)", "race_time"),
            ("Average Lap Time (mm:ss.mss)", "average_lap_time")
        ])

        # --- Strategy Section ---
        strategy_section = self.create_section("🛠 Strategy Section", [
            ("Strategy A (laps)", "strategy_a"),
            ("Strategy B (laps)", "strategy_b"),
            ("Strategy C (laps)", "strategy_c"),
            ("Strategy D (laps)", "strategy_d")
        ])

        # --- Pit Stop Section ---
        pitstop_section = self.create_section("🏎️ Pit Stop Section", [
            ("Fuel Time (sec)", "fuel_time"),
            ("Tire Time (sec)", "tire_time"),
            ("Pit Lane Time (sec)", "pit_lane_time")
        ])

        # --- Consumption Section ---
        consumption_section = self.create_section("⚡ Consumption Section", [
            ("Fuel Consumption per Lap (L)", "fuel_consumption"),
            ("Virtual Fuel per Lap (L)", "virtual_fuel"),
            ("Tire Consumption per Lap (%)", "tire_consumption")
        ])

        sections_layout = QHBoxLayout()
        sections_layout.addWidget(time_section)
        sections_layout.addWidget(strategy_section)
        sections_layout.addWidget(pitstop_section)
        sections_layout.addWidget(consumption_section)

        main_layout.addLayout(sections_layout)

        # ✅ Butonlar: Calculate, Save, Load
        self.calculate_button = QPushButton("⚙️ Calculate Strategy")
        self.save_button = QPushButton("💾 Save Strategy")
        self.load_button = QPushButton("📂 Load Strategy")

        for btn in [self.calculate_button, self.save_button, self.load_button]:
            btn.setFixedSize(230, 50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    filter: brightness(110%);
                }
            """)

        self.calculate_button.setStyleSheet(self.calculate_button.styleSheet() + """
            QPushButton {
                background-color: #ffd700;
                color: black;
            }
        """)
        self.save_button.setStyleSheet(self.save_button.styleSheet() + """
            QPushButton {
                background-color: #28a745;
                color: white;
            }
        """)
        self.load_button.setStyleSheet(self.load_button.styleSheet() + """
            QPushButton {
                background-color: #007bff;
                color: white;
            }
        """)

        self.calculate_button.clicked.connect(self.send_data)

        # ✅ Butonları yatay hizala
        button_row = QHBoxLayout()
        button_row.setSpacing(16)
        button_row.addWidget(self.calculate_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.load_button)

        main_layout.addLayout(button_row)

        # 🔗 FCY hesaplamalarında kullanılacak doğrudan erişim
        self.strategy_inputs = {
            "strategy_a": self.inputs["strategy_a"],
            "strategy_b": self.inputs["strategy_b"],
            "strategy_c": self.inputs["strategy_c"],
            "strategy_d": self.inputs["strategy_d"]
        }

        self.avg_lap_time         = self.inputs["average_lap_time"]
        self.fuel_time            = self.inputs["fuel_time"]
        self.tire_time            = self.inputs["tire_time"]
        self.pit_lane_time        = self.inputs["pit_lane_time"]
        self.fuel_per_lap         = self.inputs["fuel_consumption"]
        self.virtual_fuel_per_lap = self.inputs["virtual_fuel"]
        self.tire_consumption     = self.inputs["tire_consumption"]
        self.lap_time = self.inputs["average_lap_time"]

        # 🔗 FCY strateji erişimi için direkt bağlantılar (virgül düzeltmeli)
        self.fuel_per_lap = lambda: float(self.inputs["fuel_consumption"].text().replace(",", "."))
        self.lap_time = lambda: self.inputs["average_lap_time"].text().replace(",", ".")
        self.pit_time = lambda: float(self.inputs["pit_lane_time"].text().replace(",", "."))
        self.fuel_time = lambda: float(self.inputs["fuel_time"].text().replace(",", "."))
        self.tire_time = lambda: float(self.inputs["tire_time"].text().replace(",", "."))
        self.virtual_fuel_per_lap = lambda: float(self.inputs["virtual_fuel"].text().replace(",", "."))
        self.tire_consumption = lambda: float(self.inputs["tire_consumption"].text().replace(",", "."))

    def create_section(self, title, fields):
        outer_widget = QWidget()
        outer_widget.setObjectName("SectionCard")
        outer_widget.setStyleSheet("""
            background-color: rgba(30, 30, 30, 0.7);
            border-radius: 10px;
            padding: 0px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        outer_layout = QVBoxLayout(outer_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            border-bottom: 2px solid #ffd700;
            padding-bottom: 10px;
            margin-bottom: 20px;
        """)
        section_layout.addWidget(title_label)

        placeholder_examples = {
            "race_time": "02:00:00",
            "average_lap_time": "01:35.678",
            "strategy_a": "22",
            "strategy_b": "24",
            "strategy_c": "20",
            "strategy_d": "25",
            "fuel_time": "33,4",
            "tire_time": "24,0",
            "pit_lane_time": "32,5",
            "fuel_consumption": "2,33",
            "virtual_fuel": "2,20",
            "tire_consumption": "1,80"
        }

        for field_text, field_name in fields:
            label = QLabel(field_text)
            label.setFixedHeight(20)
            label.setStyleSheet("color: white; font-size: 16px;")
            input_field = QLineEdit()
            input_field.setFixedHeight(35)
            input_field.setPlaceholderText(placeholder_examples.get(field_name, ""))
            if field_name not in ["strategy_a", "strategy_b", "strategy_c", "strategy_d"]:
                input_field.setText(placeholder_examples.get(field_name, ""))
            input_field.setStyleSheet("""
                background-color: #2a2a2a;
                color: white;
                font-size: 16px;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #444;
            """)
            self.inputs[field_name] = input_field
            section_layout.addWidget(label)
            section_layout.addWidget(input_field)

        outer_layout.addLayout(section_layout)

        outer_widget.setFixedHeight(600)

        return outer_widget

    def send_data(self):
        try:
            strategy_values = [self.inputs[s].text().strip() for s in ["strategy_a", "strategy_b", "strategy_c", "strategy_d"]]
            if all(not val for val in strategy_values):
                QMessageBox.warning(self, "Input Error", "Lütfen en az bir strateji değeri girin (A, B, C veya D).")
                return

            data = {}
            data["json_key"] = os.path.splitext(os.path.basename(self.get_current_filename()))[0]
            data["race_time_seconds"] = parse_race_time(self.inputs["race_time"].text())
            data["average_lap_time_seconds"] = parse_average_lap_time(self.inputs["average_lap_time"].text())
            for strategy in ["strategy_a", "strategy_b", "strategy_c", "strategy_d"]:
                data[strategy] = parse_integer(self.inputs[strategy].text())
            for pit in ["fuel_time", "tire_time", "pit_lane_time"]:
                data[pit] = parse_float_one_decimal(self.inputs[pit].text())
            for consumption in ["fuel_consumption", "virtual_fuel", "tire_consumption"]:
                data[consumption] = parse_float_two_decimal(self.inputs[consumption].text())

            self.data_ready.emit(data)
            self.save_data_to_file()
        except Exception as e:
            print(f"Input Error: {e}")

    def set_current_context(self, category, brand, track):
        """Dropdown'dan gelen class, car, track bilgilerini alır ve dosyadan yükleme yapar."""
        self.current_class = category
        self.current_car = brand
        self.current_track = track
        self.load_data_from_file(category, brand, track)

    def get_current_filename(self):
        filename = f"{self.current_class}_{self.current_car}_{self.current_track}".lower().replace(" ", "")
        return os.path.join("data", "strategy_inputs", f"{filename}.json")

    def load_data_from_file(self, category, brand, track):
        """Kayıtlı form verilerini JSON dosyasından yükler."""
        self.current_class = category
        self.current_car = brand
        self.current_track = track
        filename = self.get_current_filename()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for key, field in self.inputs.items():
                if key in saved:
                    field.setText(saved[key])

    def save_data_to_file(self):
        """Kullanıcının form girdilerini JSON dosyasına kaydeder, diğer verileri silmez."""
        os.makedirs(os.path.join("data", "strategy_inputs"), exist_ok=True)
        filename = self.get_current_filename()

        # 🔁 Önceki veriyi oku
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(">>> Uyarı: JSON hatalı, boş veri ile devam ediliyor")
                    data = {}
        else:
            data = {}

        # 🔁 Form alanlarını güncelle
        for key, field in self.inputs.items():
            data[key] = field.text()

        # 🔁 Diğer alanlara dokunulmadan kaydet
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_strategy_data(self):
        return {
            "race_time": self.race_time(),
            "average_lap_time": self.lap_time(),
            "strategy_a": self.strategy_inputs["strategy_a"].text(),
            "strategy_b": self.strategy_inputs["strategy_b"].text(),
            "strategy_c": self.strategy_inputs["strategy_c"].text(),
            "strategy_d": self.strategy_inputs["strategy_d"].text(),
            "fuel_time": self.fuel_time(),
            "tire_time": self.tire_time(),
            "pit_lane_time": self.pit_time(),
            "fuel_consumption": self.fuel_per_lap(),
            "virtual_fuel": self.virtual_fuel_per_lap(),
            "tire_consumption": self.tire_consumption(),
            "driver_assignments": self.get_driver_assignments(),
        }


    def race_time(self):
        return self.inputs["race_time"].text()

    def lap_time(self):
        return self.inputs["average_lap_time"].text()

    def fuel_time(self):
        return self.inputs["fuel_time"].text()

    def tire_time(self):
        return self.inputs["tire_time"].text()

    def pit_time(self):
        return self.inputs["pit_lane_time"].text()

    def fuel_per_lap(self):
        return self.inputs["fuel_consumption"].text()

    def virtual_fuel_per_lap(self):
        return self.inputs["virtual_fuel"].text()

    def tire_consumption(self):
        return self.inputs["tire_consumption"].text()

    def team(self):
        return self.inputs["team"].text()

    def get_driver_assignments(self):
        return self.driver_assignments if hasattr(self, "driver_assignments") else {}

    def get_json_key(self):
        class_name = self.inputs["class"].currentText().strip().lower()
        car_name = self.inputs["car"].currentText().strip().lower()
        track_name = self.inputs["track"].currentText().strip().lower()
        return f"{class_name}_{car_name}_{track_name}"



