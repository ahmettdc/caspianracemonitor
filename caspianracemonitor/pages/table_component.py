from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QLabel, QHeaderView, QFrame, QHBoxLayout, QCheckBox, QPushButton, QLineEdit, QRadioButton
from PyQt6.QtCore import Qt
from pages.strategy_utils import format_time, calculate_stint_time, calculate_time_left
from ui.toggleswitch import ToggleSwitch
import os, sys, json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TableComponent(QWidget):
    detailed_mode = False

    def __init__(self, data=None):
        super().__init__()
        layout = QVBoxLayout(self)

        self.custom_pit_times = {}
        self.custom_laps = {}
        self.toggle_switch = ToggleSwitch("Toggle View", initial=True)
        self.toggle_switch.checkbox.stateChanged.connect(self.toggle_detailed_mode)

        # Toggle layout
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        toggle_layout.addWidget(self.toggle_switch)
        layout.addWidget(toggle_container)

        # Tablo
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # 🔁 Eğer data varsa strateji sütunlarını oluştur
        if data:
            strategy_keys = [k for k in ["strategy_a", "strategy_b", "strategy_c", "strategy_d"] if data.get(k, 0) > 0]
            self.table.setColumnCount(2 + len(strategy_keys))
            headers = ["Stint No", "Strategy Option"]
            headers += [k.replace("strategy_", "Strategy ").upper() for k in strategy_keys]
            self.table.setHorizontalHeaderLabels(headers)

            header = self.table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

            for i in range(2, self.table.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.table.itemSelectionChanged.connect(self.highlight_selected_rows)
        layout.addWidget(self.table)

        self.checkbox_state_by_row = {}

    def update_table(self, data):
        self.last_data = data

        # ✅ JSON'dan strategy_options yükle (varsa)
        json_key = data.get("json_key")
        if json_key:
            filename = os.path.join("data", "strategy_inputs", f"{json_key}.json")
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        saved = json.load(f)
                        if "strategy_options" in saved:
                            for row_str, opt in saved["strategy_options"].items():
                                row = int(row_str)
                                self.custom_pit_times[row] = {
                                    "tire": opt.get("tire", ""),
                                    "fuel": opt.get("fuel", ""),
                                    "tire_checked": opt.get("tire_checked", True),
                                    "fuel_checked": opt.get("fuel_checked", True)
                                }
                except Exception as e:
                    print("strategy_options yükleme hatası:", e)

        # ✅ Sütun başlıklarını burada oluştur
        strategy_keys = [k for k in ["strategy_a", "strategy_b", "strategy_c", "strategy_d"] if data.get(k, 0) > 0]
        self.table.setColumnCount(2 + len(strategy_keys))
        headers = ["Stint No", "Strategy Option"]
        headers += [k.replace("strategy_", "Strategy ").upper() for k in strategy_keys]
        self.table.setHorizontalHeaderLabels(headers)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(2, self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        strategies = [k for k in data.keys() if k.startswith("strategy_")]
        stint_counts = {s: data.get(s, 0) for s in strategies}

        race_time = data.get("race_time_seconds", 0)
        avg_lap_time = data.get("average_lap_time_seconds", 0)
        fuel_time = data.get("fuel_time", 0)
        tire_time = data.get("tire_time", 0)
        pit_lane_time = data.get("pit_lane_time", 0)
        fuel_consumption = data.get("fuel_consumption", 0)
        virtual_fuel = data.get("virtual_fuel", 0)

        estimated_total_laps = race_time / avg_lap_time if avg_lap_time > 0 else 0
        estimated_total_stints = int(estimated_total_laps) + 5
        max_stints = min(50, max(max(stint_counts.values()), estimated_total_stints))
        self.table.setRowCount(max_stints)

        elapsed_times = {s: 0 for s in strategies}
        self.checkbox_state_by_row.clear()


        for stint_num in range(max_stints):
            self.table.setCellWidget(stint_num, 0, self.create_stint_box_widget(f"{stint_num + 1}", stint_num))

            # Güncellenmiş şekilde 5 değer döndüren fonksiyon çağrısı
            tire_cb, fuel_cb, tire_input, fuel_input, container = self.create_strategy_option_box_widget(
                "", stint_num, fuel_time, tire_time, pit_lane_time
            )

            self.checkbox_state_by_row[stint_num] = {
                "tire_cb": tire_cb,
                "fuel_cb": fuel_cb,
                "tire_input": tire_input,
                "fuel_input": fuel_input
            }

            self.table.setCellWidget(stint_num, 1, container)

            # ✅ Yalnızca o satırdaki strategy hücreleri tamamen "-" ise ilk iki sütunu da "-" yap
            strategy_cells_empty = True
            for col in range(2, self.table.columnCount()):
                widget = self.table.cellWidget(stint_num, col)
                if widget:
                    label = widget.findChild(QLabel)
                    if label and label.text().strip() != "-":
                        strategy_cells_empty = False
                        break

            if strategy_cells_empty:
                self.table.setCellWidget(stint_num, 0, self.create_stint_box_widget("-", stint_num))
                self.table.setCellWidget(stint_num, 1, self.create_stint_box_widget("-", stint_num))


        for stint_num in range(max_stints):
            empty_row = True
            for col, strategy in enumerate(strategies, start=2):
                strategy_index = col - 2
                default_laps = stint_counts[strategy]
                custom_laps = self.custom_laps.get((stint_num, strategy_index), default_laps)
                total_laps = custom_laps

                if elapsed_times[strategy] < race_time:
                    planned_stint_time = calculate_stint_time(avg_lap_time, total_laps)

                    custom = self.custom_pit_times.get(stint_num, {})
                    tire_val = custom.get("tire", tire_time)
                    fuel_val = custom.get("fuel", fuel_time)
                    tire_checked = custom.get("tire_checked", True)
                    fuel_checked = custom.get("fuel_checked", True)

                    try:
                        current_tire = float(tire_val)
                    except:
                        current_tire = tire_time

                    try:
                        current_fuel = float(fuel_val)
                    except:
                        current_fuel = fuel_time

                    extra_laps = custom.get("fuel_extra_laps", 0)
                    current_fuel += fuel_consumption * extra_laps

                    # ✅ Son stint kontrolü: kalan süre bu stint sonunda doluyorsa pit atlanır
                    is_last_stint = (elapsed_times[strategy] + planned_stint_time + pit_lane_time >= race_time)

                    if is_last_stint:
                        pit_time = 0.0
                    else:
                        if not tire_checked and not fuel_checked:
                            pit_time = 0.0
                        else:
                            pit_time = pit_lane_time
                            if tire_checked:
                                pit_time += current_tire
                            if fuel_checked:
                                pit_time += current_fuel

                    max_available_stint_time = max(0, race_time - elapsed_times[strategy] - pit_time)
                    actual_stint_time = min(planned_stint_time, max_available_stint_time)
                    cumulative_time = elapsed_times[strategy] + actual_stint_time + pit_time
                    time_left = calculate_time_left(race_time, cumulative_time)

                    lap_ratio = actual_stint_time / avg_lap_time if avg_lap_time > 0 else 0
                    fuel_base = fuel_consumption * lap_ratio
                    fuel_value = fuel_base + (fuel_consumption * extra_laps)

                    self.table.setCellWidget(stint_num, col, self.create_card_widget(
                        format_time(actual_stint_time),
                        format_time(pit_time),
                        format_time(cumulative_time),
                        format_time(time_left),
                        fuel_value,
                        virtual_fuel * lap_ratio,
                        stint_num,
                        strategy_index
                    ))

                    empty_row = False
                    elapsed_times[strategy] = cumulative_time

                else:
                    self.table.setCellWidget(stint_num, col, self.create_stint_box_widget("-", stint_num))

            # ✅ Koşullu "-" kontrolü sadece strateji hücrelerinin tamamı "-" ise yapılır
            strategy_cells_empty = True
            for col in range(2, self.table.columnCount()):
                widget = self.table.cellWidget(stint_num, col)
                if widget:
                    label = widget.findChild(QLabel)
                    if label and label.text().strip() != "-":
                        strategy_cells_empty = False
                        break

            if strategy_cells_empty:
                self.table.setCellWidget(stint_num, 0, self.create_stint_box_widget("-", stint_num))
                self.table.setCellWidget(stint_num, 1, self.create_stint_box_widget("-", stint_num))

        if all(self.is_empty_row(row) for row in range(self.table.rowCount())):
            self.setVisible(False)
        else:
            self.table.show()

        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        height = sum([self.table.rowHeight(i) for i in range(self.table.rowCount())])
        self.table.setMinimumHeight(height + self.table.horizontalHeader().height())

        # ✅ Calculate sonrası sütunları yay
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Stint No
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Strategy Option

        # 🔁 Sadece var olan strateji sütunlarını yay
        col_count = self.table.columnCount()
        for i in range(2, col_count):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # ✅ JSON'a kaydetmeden önce tüm hücrelerden en güncel verileri çek
        for row, state in self.checkbox_state_by_row.items():
            self.custom_pit_times[row] = {
                "tire": state["tire_input"].text(),
                "fuel": state["fuel_input"].text(),
                "tire_checked": state["tire_cb"].isChecked(),
                "fuel_checked": state["fuel_cb"].isChecked(),
                "fuel_extra_laps": self.custom_pit_times.get(row, {}).get("fuel_extra_laps", 0)
            }

        # ✅ JSON'a kaydet
        if "json_key" in data:
            self.save_to_json(os.path.join("data", "strategy_inputs", f"{data['json_key']}.json"))

    def create_stint_box_widget(self, text, row_index):
        card = QLabel(text)
        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet(f"""
            background-color: {'rgba(0,0,0,0.9)' if row_index % 2 == 0 else 'rgba(0,0,0,0.4)'};
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Poppins';
        """)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(card)
        return container

    def create_strategy_option_box_widget(self, text, row_index, fuel_time=0.0, tire_time=0.0, pit_lane_time=0.0):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        container.setObjectName("StrategyOptionContainer")


        checkbox_row = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_row)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(10)
        

        tire_checkbox = QCheckBox("TireTime")
        fuel_checkbox = QCheckBox("FuelTime")

        tire_checked = self.custom_pit_times.get(row_index, {}).get("tire_checked", True)
        fuel_checked = self.custom_pit_times.get(row_index, {}).get("fuel_checked", True)
        tire_checkbox.setChecked(tire_checked)
        fuel_checkbox.setChecked(fuel_checked)


        checkbox_layout.addWidget(tire_checkbox)

        tire_val = self.custom_pit_times.get(row_index, {}).get("tire", tire_time)
        fuel_val = self.custom_pit_times.get(row_index, {}).get("fuel", fuel_time)

        tire_input = QLineEdit(str(tire_val))
        tire_input.setFixedWidth(50)
        tire_input.setVisible(self.detailed_mode)
        checkbox_layout.addWidget(tire_input)

        checkbox_layout.addWidget(fuel_checkbox)

        fuel_input = QLineEdit(str(fuel_val))
        fuel_input.setFixedWidth(50)
        fuel_input.setVisible(self.detailed_mode)
        checkbox_layout.addWidget(fuel_input)

                # 🟥 Kart 1: Pit Components
        pit_card = QWidget()
        pit_card_layout = QVBoxLayout(pit_card)
        pit_card_layout.setContentsMargins(8, 8, 8, 8)
        pit_card_layout.setSpacing(6)

        pit_card.setStyleSheet("""
            background-color: rgba(80, 80, 80, 0.4);
            border-radius: 10px;
            padding-left: 8px;
        """)

        pit_label = QLabel("Pit Components")
        pit_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        pit_card_layout.addWidget(pit_label)

        # Mevcut checkbox satırını bu karta ekliyoruz
        pit_card_layout.addWidget(checkbox_row)

        # Bu kartı ana layout'a ekliyoruz
        layout.addWidget(pit_card)

        pit_time_label = QLabel()
        # 🟩 Kart 2: Total Pit Time
        pit_time_card = QWidget()
        pit_time_card_layout = QVBoxLayout(pit_time_card)
        pit_time_card_layout.setContentsMargins(8, 8, 8, 8)
        pit_time_card_layout.setSpacing(6)

        pit_time_card.setStyleSheet("""
            background-color: rgba(60, 60, 60, 0.4);
            border-radius: 10px;
            padding-left: 8px;
        """)

        pit_time_title = QLabel("Total Pit Time")
        pit_time_title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        pit_time_card_layout.addWidget(pit_time_title)

        pit_time_card_layout.addWidget(pit_time_label)

        layout.addWidget(pit_time_card)

        pit_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pit_time_label.setObjectName("PitTimeLabel")

        def save_custom_state():
            self.custom_pit_times.setdefault(row_index, {})
            self.custom_pit_times[row_index].update({
                "tire": tire_input.text(),
                "fuel": fuel_input.text(),
                "tire_checked": tire_checkbox.isChecked(),
                "fuel_checked": fuel_checkbox.isChecked()
            })

        def update_pit_time():
            try:
                current_tire = float(self.custom_pit_times.get(row_index, {}).get("tire", tire_time))
            except:
                current_tire = tire_time
            try:
                current_fuel = float(self.custom_pit_times.get(row_index, {}).get("fuel", fuel_time))
            except:
                current_fuel = fuel_time

            if not tire_checkbox.isChecked() and not fuel_checkbox.isChecked():
                total = 0.0
            else:
                total = pit_lane_time
                if tire_checkbox.isChecked():
                    total += current_tire
                if fuel_checkbox.isChecked():
                    total += current_fuel

            pit_time_label.setText(f"Total Pit Time: {total:.1f}s")


        # Event bağlantıları
        tire_input.textChanged.connect(lambda: [save_custom_state(), update_pit_time()])
        fuel_input.textChanged.connect(lambda: [save_custom_state(), update_pit_time()])
        tire_checkbox.stateChanged.connect(lambda: [save_custom_state(), update_pit_time()])
        fuel_checkbox.stateChanged.connect(lambda: [save_custom_state(), update_pit_time()])

        update_pit_time()

        # 🟦 Kart 3: Extra Fuel Lap
        extra_card = QWidget()
        extra_card_layout = QVBoxLayout(extra_card)
        extra_card_layout.setContentsMargins(8, 8, 8, 8)
        extra_card_layout.setSpacing(6)

        extra_card.setStyleSheet("""
            background-color: rgba(40, 40, 40, 0.3);
            border-radius: 10px;
            padding-left: 8px;
        """)

        extra_label = QLabel("Extra Fuel Lap")
        extra_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        extra_card_layout.addWidget(extra_label)

        extra_group = QWidget()
        extra_layout = QHBoxLayout(extra_group)
        extra_layout.setContentsMargins(0, 0, 0, 0)
        extra_layout.setSpacing(5)

        radio_buttons = []
        for i in range(0, 4):  # 0 dahil edildi
            btn = QRadioButton(f"+{i}")
            btn.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-size: 12px;
                }
                QRadioButton::indicator {
                    width: 14px;
                    height: 14px;
                    border-radius: 7px;
                    border: 2px solid white;
                    background-color: transparent;
                }
                QRadioButton::indicator:checked {
                    background-color: #FFD700;
                    border: 2px solid #FFD700;
                }
            """)
            radio_buttons.append(btn)
            extra_layout.addWidget(btn)

        current_extra = self.custom_pit_times.get(row_index, {}).get("fuel_extra_laps", 0)
        if current_extra in [0, 1, 2, 3]:
            radio_buttons[current_extra].setChecked(True)

        def on_extra_changed():
            self.custom_pit_times.setdefault(row_index, {})
            for i, btn in enumerate(radio_buttons):
                if btn.isChecked():
                    self.custom_pit_times[row_index]["fuel_extra_laps"] = i  # i artık doğrudan 0, 1, 2, 3
                    break
            self.update_table_from_checkbox(row_index)

        for btn in radio_buttons:
            btn.toggled.connect(on_extra_changed)

        extra_card_layout.addWidget(extra_group)
        layout.addWidget(extra_card)

        # ✅ Bileşenleri kaydet (adım 4)
        self.checkbox_state_by_row[row_index] = {
            "tire_cb": tire_checkbox,
            "fuel_cb": fuel_checkbox,
            "tire_input": tire_input,
            "fuel_input": fuel_input
        }

        return tire_checkbox, fuel_checkbox, tire_input, fuel_input, container


    def toggle_detailed_mode(self, checked):
        self.detailed_mode = checked
        if hasattr(self, 'last_data'):
            self.update_table(self.last_data)

    def create_card_widget(self, stint, pit, total, remaining, fuel, virtual, row_index, strategy_index):
        outer_card = QWidget()
        outer_layout = QVBoxLayout(outer_card)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(5)

        shade = "rgba(0, 0, 0, 0.9)" if row_index % 2 == 0 else "rgba(0, 0, 0, 0.4)"
        outer_card.setStyleSheet(f"""
            background-color: {shade};
            border-radius: 10px;
            margin-bottom: 5px;
        """)

        
        outer_layout.addWidget(self.create_labeled_block("Stint Time", stint, "#1E90FF"))
        outer_layout.addWidget(self.create_divider())
        outer_layout.addWidget(self.create_labeled_block("Pit Time", pit, "#FFD700"))
        outer_layout.addWidget(self.create_divider())
        outer_layout.addWidget(self.create_labeled_block("Total Time", total, "#708090"))
        outer_layout.addWidget(self.create_divider())
        outer_layout.addWidget(self.create_labeled_block("Remaining", remaining, "#FF6347"))
        outer_layout.addWidget(self.create_divider())

        fuel_row = QWidget()
        fuel_layout = QHBoxLayout(fuel_row)
        fuel_layout.setContentsMargins(0, 0, 0, 0)
        fuel_layout.setSpacing(5)
        fuel_label = self.create_labeled_block("Fuel", f"{fuel:.2f}L", "#32CD32")
        virtual_label = self.create_labeled_block("Virtual", f"{virtual:.2f}%", "#9370DB")
        fuel_layout.addWidget(fuel_label)
        fuel_layout.addWidget(virtual_label)
        outer_layout.addWidget(fuel_row)

        # stint lap input (sadece detaylı modda görünür)
        if self.detailed_mode:
            lap_input = QLineEdit()
            lap_input.setPlaceholderText("laps")
            lap_input.setFixedWidth(50)
            lap_input.setStyleSheet("""
                background-color: #222;
                color: white;
                font-size: 12px;
                padding: 4px;
                border: 1px solid #555;
                border-radius: 4px;
            """)
            current_value = self.custom_laps.get((row_index, strategy_index), "")
            lap_input.setText(str(current_value) if current_value else "")
            lap_input.textChanged.connect(lambda: self.save_custom_lap_input(row_index, strategy_index, lap_input.text()))
            outer_layout.addWidget(lap_input, alignment=Qt.AlignmentFlag.AlignCenter)

        return outer_card

    def create_labeled_block(self, label, value, bg_color):
        icons = {
            "Stint Time": "clock.png",
            "Pit Time": "pitstop_sign.png",
            "Total Time": "hourglass.png",
            "Remaining": "time_remaining.png",
            "Fuel": "fuel_can.png",
            "Virtual": "lightning.png"
        }
        icon_file = icons.get(label)
        icon_path = resource_path(f"assets/icons/{icon_file}") if icon_file else None

        block = QLabel()
        if icon_path and os.path.exists(icon_path):
            block.setText(f'<img src="{icon_path}" width="14" height="14"> {label}: {value}')
        else:
            block.setText(f"{label}: {value}")
        block.setAlignment(Qt.AlignmentFlag.AlignCenter)
        block.setStyleSheet(f"""
            background-color: {self.hex_to_rgba(bg_color, 0.8)};
            border-radius: 6px;
            margin-bottom: 5px;
            padding: 8px;
            color: white;
            font-family: 'Poppins';
            font-size: 13px;
            font-weight: 600;
        """)
        return block

    def create_divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("""
            color: rgba(255, 140, 0, 0.8);
            background-color: rgba(255, 140, 0, 0.8);
            height: 2px;
            margin-top: 3px;
            margin-bottom: 3px;
            border: none;
        """)
        return line

    def highlight_selected_rows(self):
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        for row in range(self.table.rowCount()):
            is_selected = row in selected_rows
            for col in range(self.table.columnCount()):
                widget = self.table.cellWidget(row, col)
                if widget:
                    if is_selected:
                        widget.setStyleSheet("background-color: rgba(255, 215, 0, 0.2); border-radius: 10px;")
                    else:
                        shade = "rgba(0, 0, 0, 0.9)" if row % 2 == 0 else "rgba(0, 0, 0, 0.4)"
                        widget.setStyleSheet(f"background-color: {shade}; border-radius: 10px;")

    def is_last_stint_for_strategy(self, stint_index, strategy, total_planned_stints):
        return stint_index == total_planned_stints - 1

    def update_table_from_checkbox(self, row_index):
        data = getattr(self, 'last_data', None)
        if not data:
            return

        strategies = ["strategy_a", "strategy_b", "strategy_c", "strategy_d"]
        fuel_time = data.get("fuel_time", 0)
        tire_time = data.get("tire_time", 0)
        pit_lane_time = data.get("pit_lane_time", 0)
        avg_lap_time = data.get("average_lap_time_seconds", 0)
        race_time = data.get("race_time_seconds", 0)
        fuel_consumption = data.get("fuel_consumption", 0)
        virtual_fuel = data.get("virtual_fuel", 0)

        elapsed_times = {s: 0 for s in strategies}
        for stint_num in range(row_index + 1):
            for col, strategy in enumerate(strategies, start=2):
                strategy_index = col - 2  # Strategy A=0, B=1, C=2, D=3
                default_laps = data.get(strategy, 0)
                custom_laps = self.custom_laps.get((stint_num, strategy_index), default_laps)
                total_laps = custom_laps

                if elapsed_times[strategy] < race_time:
                    planned_stint_time = calculate_stint_time(avg_lap_time, total_laps)

                    # ✅ Pit ayarları
                    custom = self.custom_pit_times.get(stint_num, {})
                    tire_val = custom.get("tire", tire_time)
                    fuel_val = custom.get("fuel", fuel_time)
                    tire_checked = custom.get("tire_checked", True)
                    fuel_checked = custom.get("fuel_checked", True)

                    try:
                        current_tire = float(tire_val)
                    except:
                        current_tire = tire_time

                    try:
                        current_fuel = float(fuel_val)
                    except:
                        current_fuel = fuel_time

                    extra_laps = custom.get("fuel_extra_laps", 0)
                    current_fuel += fuel_consumption * extra_laps

                    # 🔍 Son stint kontrolü
                    is_last_stint = (elapsed_times[strategy] + planned_stint_time + pit_lane_time >= race_time)

                    if is_last_stint:
                        pit_time = 0.0
                    else:
                        if not tire_checked and not fuel_checked:
                            pit_time = 0.0
                        else:
                            pit_time = pit_lane_time
                            if tire_checked:
                                pit_time += current_tire
                            if fuel_checked:
                                pit_time += current_fuel

                    max_available_stint_time = max(0, race_time - elapsed_times[strategy] - pit_time)
                    actual_stint_time = min(planned_stint_time, max_available_stint_time)
                    cumulative_time = elapsed_times[strategy] + actual_stint_time + pit_time
                    time_left = calculate_time_left(race_time, cumulative_time)

                    lap_ratio = actual_stint_time / avg_lap_time if avg_lap_time > 0 else 0
                    fuel_base = fuel_consumption * lap_ratio
                    fuel_value = fuel_base + (fuel_consumption * extra_laps)

                    self.table.setCellWidget(stint_num, col, self.create_card_widget(
                        format_time(actual_stint_time),
                        format_time(pit_time),
                        format_time(cumulative_time),
                        format_time(time_left),
                        fuel_value,
                        virtual_fuel * lap_ratio,
                        stint_num,
                        strategy_index
                    ))

                    elapsed_times[strategy] = cumulative_time

    def save_custom_lap_input(self, row_index, strategy_index, text):
        try:
            value = int(text)
            if value > 0:
                self.custom_laps[(row_index, strategy_index)] = value
            else:
                self.custom_laps.pop((row_index, strategy_index), None)
        except ValueError:
            self.custom_laps.pop((row_index, strategy_index), None)

        # ❌ Artık anlık güncelleme yok
        # self.update_table(self.last_data)


    def hex_to_rgba(self, hex_color, alpha):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2 ,4))
        return f'rgba({r}, {g}, {b}, {alpha})'
    
    def is_empty_row(self, row):
        for col in range(self.table.columnCount()):
            widget = self.table.cellWidget(row, col)
            if widget:
                label = widget.findChild(QLabel)
                if label and label.text().strip() != "-":
                    return False
        return True
    
    def get_strategy_data_for_drivers(self, strategy_name):
        index_map = {
            "strategy_a": 2,
            "strategy_b": 3,
            "strategy_c": 4,
            "strategy_d": 5
        }
        col_index = index_map.get(strategy_name)
        if col_index is None:
            return []

        result = []
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, col_index)
            if widget:
                # Varsayılanlar
                stint, pit, total, fuel, virtual = "00:00:00", "00:00", "00:00:00", 0.0, 0.0
                for lbl in widget.findChildren(QLabel):
                    txt = lbl.text()
                    if "Stint Time" in txt:
                        stint = txt.split(": ")[-1]
                    elif "Pit Time" in txt:
                        pit = txt.split(": ")[-1]
                    elif "Total Time" in txt:
                        total = txt.split(": ")[-1]
                    elif "Fuel" in txt:
                        try: fuel = float(txt.split()[1].replace("L", ""))
                        except: fuel = 0.0
                    elif "Virtual" in txt:
                        try: virtual = float(txt.split()[1].replace("%", ""))
                        except: virtual = 0.0

                result.append({
                    "stint": stint,
                    "pit": pit,
                    "total": total,
                    "fuel": fuel,
                    "virtual": virtual,
                    "row": row
                })
        return result
    
    def get_recreated_card_widget(self, data: dict, row_index: int, strategy_index: int = 0):
        return self.create_card_widget(
            data["stint"],
            data["pit"],
            data["total"],
            "00:00:00",  # remaining
            data["fuel"],
            data["virtual"],
            row_index,
            strategy_index
        )

    def save_to_json(self, filename: str):
        strategy_data = self.get_strategy_option_state()

        try:
            # 🔁 Mevcut dosyayı oku (varsa)
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}
        except Exception as e:
            print("⚠ JSON okuma hatası:", e)
            data = {}

        # 🔁 Strategy Options bölümünü güncelle
        data["strategy_options"] = strategy_data

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✔ Strategy options saved to: {filename}")
        except Exception as e:
            print("❌ JSON yazma hatası:", e)

    def get_strategy_option_state(self):
        strategy_data = {}

        for row, values in self.custom_pit_times.items():
            strategy_data[str(row)] = {
                "tire": values.get("tire", ""),
                "fuel": values.get("fuel", ""),
                "tire_checked": values.get("tire_checked", True),
                "fuel_checked": values.get("fuel_checked", True)
            }

        return strategy_data
    
    def save_strategy_data(self, json_key):
        path = os.path.join("data", "strategy_inputs", f"{json_key}.json")
        strategy_data = self.get_strategy_option_state()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}

        data["strategy_options"] = strategy_data
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✔ Saved to {path}")

    def load_strategy_data(self, json_key):
        path = os.path.join("data", "strategy_inputs", f"{json_key}.json")
        if not os.path.exists(path):
            print(f"⚠ No strategy data at {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "strategy_options" not in data:
            print("⚠ No strategy_options in file.")
            return

        for row_str, opt in data["strategy_options"].items():
            row = int(row_str)
            self.custom_pit_times[row] = {
                "tire": opt.get("tire", ""),
                "fuel": opt.get("fuel", ""),
                "tire_checked": opt.get("tire_checked", True),
                "fuel_checked": opt.get("fuel_checked", True),
                "fuel_extra_laps": self.custom_pit_times.get(row, {}).get("fuel_extra_laps", 0)
            }

        # ✅ Yeniden çiz
        if hasattr(self, "last_data"):
            self.update_table(self.last_data)

    def generate_fcy_strategy_column(self, stint_count: int, stint_minutes: int, total_remaining_secs: int):
        from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout
        from PyQt6.QtCore import Qt

        col_index = 6  # FCY öneri kolonu (gerekirse dinamik yapabilirsin)
        self.table.setColumnCount(max(self.table.columnCount(), col_index + 1))
        self.table.setRowCount(stint_count)

        cumulative_secs = 0

        for i in range(stint_count):
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)

            # Süreler
            stint_secs = stint_minutes * 60
            pit_secs = 75  # 1:15 sabit pit
            total_secs = stint_secs + pit_secs
            cumulative_secs += total_secs

            # Remaining hesapla
            remaining_secs = max(0, total_remaining_secs - cumulative_secs)
            rem_h = remaining_secs // 3600
            rem_m = (remaining_secs % 3600) // 60
            rem_s = remaining_secs % 60

            # ⛽ Fuel hesapla
            laps_per_stint = stint_secs // 90  # varsayım: 1 tur = 90s
            fuel_per_lap = 2.5  # örnek sabit
            fuel_total = laps_per_stint * fuel_per_lap

            # 🧱 Hücre içeriği
            stint_label = QLabel(f"Stint {i + 1}")
            stint_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold; font-family: Poppins;")

            stint_time = QLabel(f"🕒 Stint Time: 00:{stint_minutes:02}:00")
            stint_time.setStyleSheet("color: #00BFFF; font-size: 13px; font-family: Poppins;")

            pit_time = QLabel("🔧 Pit Time: 00:01:15")
            pit_time.setStyleSheet("color: #FFD700; font-size: 13px; font-family: Poppins;")

            total_time = QLabel(f"⏱ Total Time: {total_secs // 60:02}:{total_secs % 60:02}")
            total_time.setStyleSheet("color: silver; font-size: 13px; font-family: Poppins;")

            remaining = QLabel(f"⏳ Remaining: {rem_h:02}:{rem_m:02}:{rem_s:02}")
            remaining.setStyleSheet("color: #FF6666; font-size: 13px; font-family: Poppins;")

            fuel = QLabel(f"⛽ {fuel_total:.2f}L")
            virtual = QLabel("🟣 130.00%")

            for lbl in (fuel, virtual):
                lbl.setStyleSheet("color: white; font-size: 13px; font-family: Poppins;")

            h = QWidget()
            h_layout = QHBoxLayout(h)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(6)
            h_layout.addWidget(fuel)
            h_layout.addWidget(virtual)

            # 🎯 Eklemeler
            layout.addWidget(stint_label)
            layout.addWidget(stint_time)
            layout.addWidget(pit_time)
            layout.addWidget(total_time)
            layout.addWidget(remaining)
            layout.addWidget(h)

            self.table.setCellWidget(i, col_index, container)














