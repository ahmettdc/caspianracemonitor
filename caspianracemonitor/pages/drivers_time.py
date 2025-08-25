from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QLabel, QDateTimeEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QPushButton, QHeaderView, QSizePolicy, QLineEdit, QCheckBox
)
from PyQt6.QtCore import QDateTime, Qt, QTime
from PyQt6.QtGui import QPalette, QColor, QBrush
import os, json

class EditableLabel(QLineEdit):
    def __init__(self, initial_text, parent=None):
        self.strategy_selected_callback = None
        super().__init__(parent)
        self.setText(initial_text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-family: Poppins;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.setReadOnly(True)

    def mouseDoubleClickEvent(self, event):
        self.setReadOnly(False)
        self.selectAll()
        self.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: #222;
                border: 1px solid #ffd700;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
                font-family: Poppins;
                font-size: 14px;
            }
        """)
        self.setFocus()

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        self.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-family: Poppins;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }
        """)
        super().focusOutEvent(event)

class DriversTimePage(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_strategy = "strategy_a"
        self.pilot_list = []

        layout = QVBoxLayout(self)

        self.radio_group = QButtonGroup(self)
        keys = ["strategy_a", "strategy_b", "strategy_c", "strategy_d"]

        strategy_widget = QWidget()
        strategy_layout = QHBoxLayout(strategy_widget)
        strategy_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        strategy_layout.setContentsMargins(0, 0, 0, 0)
        strategy_layout.setSpacing(6)

        strategy_label = QLabel("Select Strategy:")
        strategy_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        strategy_label.setStyleSheet("""
            color: white;
            font-family: Poppins;
            font-size: 14px;
            margin: 0px;
            padding: 0px;
        """)
        strategy_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Genişlik otomatik, sıkışmaz
        strategy_layout.addWidget(strategy_label)

        for key in keys:
            radio = QRadioButton(key.replace("_", " ").title())
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    font-weight: bold;
                    font-size: 13px;
                }
                QRadioButton::indicator {
                    width: 14px;
                    height: 14px;
                }
                QRadioButton::indicator:checked {
                    background-color: #ffd700;
                    border: 2px solid #ffaa00;
                    border-radius: 7px;
                }
                QRadioButton::indicator:unchecked {
                    background-color: #444;
                    border: 1px solid #666;
                    border-radius: 7px;
                }
            """)
            radio.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Genişliği içeriğe sabitle
            if key == self.selected_strategy:
                radio.setChecked(True)
            self.radio_group.addButton(radio)
            strategy_layout.addWidget(radio)

        layout.addWidget(strategy_widget)
        self.radio_group.buttonClicked.connect(self.on_strategy_changed)

        # 🔄 RST ve TEAM hizalı tek satır
        form_row = QWidget()
        form_row_layout = QHBoxLayout(form_row)
        form_row_layout.setContentsMargins(0, 0, 0, 0)
        form_row_layout.setSpacing(20)

        # 🕓 RST Alanı
        rst_group = QWidget()
        rst_layout = QHBoxLayout(rst_group)
        rst_layout.setContentsMargins(0, 0, 0, 0)
        rst_layout.setSpacing(6)
        form_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        rst_label = QLabel("RST:")
        rst_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        rst_label.setFixedWidth(40)
        rst_label.setStyleSheet("""
            color: white;
            font-family: Poppins;
            font-size: 14px;
        """)

        self.race_start_picker = QDateTimeEdit()
        self.race_start_picker.setDisplayFormat("dd MMM yyyy HH:mm")
        self.race_start_picker.setDateTime(QDateTime.currentDateTime())
        self.race_start_picker.setFixedWidth(200)
        self.race_start_picker.lineEdit().setMaximumWidth(200)
        self.race_start_picker.setStyleSheet("""
            QDateTimeEdit {
                background-color: rgba(40, 40, 40, 0.5);
                color: white;
                border: 1px solid #ffd700;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QDateTimeEdit QLineEdit {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)

        rst_layout.addWidget(rst_label)
        rst_layout.addWidget(self.race_start_picker)

        # 🏁 TEAM Alanı
        self.team_selector = QComboBox()
        self.team_selector.setFixedWidth(250)
        self.team_selector.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #ffd700;
            }
        """)
        self.team_selector.currentTextChanged.connect(self.set_current_team)
        self.load_teams_to_dropdown()

        team_group = QWidget()
        team_layout = QHBoxLayout(team_group)
        team_layout.setContentsMargins(0, 0, 0, 0)
        team_layout.setSpacing(6)

        team_label = QLabel("Team:")
        team_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        team_label.setFixedWidth(50)
        team_label.setStyleSheet("""
            color: white;
            font-family: Poppins;
            font-size: 14px;
        """)

        team_layout.addWidget(team_label)
        team_layout.addWidget(self.team_selector)

        # 🧩 Satırda hizalı şekilde ekle
        form_row_layout.addWidget(rst_group)
        form_row_layout.addWidget(team_group)

        # Ana layout’a ekle
        layout.addWidget(form_row)



        # 🟡 Calculate + Warning birlikte yatay layout
        calculate_row = QHBoxLayout()

        calculate_button = QPushButton("Calculate")
        calculate_button.setFixedWidth(300)
        calculate_button.setStyleSheet(""" 
            QPushButton {
                background-color: #ffd700;
                color: black;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 8px;
                font-family: Poppins;
                font-size: 14px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #ffe033;
            }
            QPushButton:pressed {
                background-color: #e6c200;
            }
        """)
        calculate_button.clicked.connect(self.on_calculate_clicked)
        save_button = QPushButton("Save Data")
        load_button = QPushButton("Load Data")

        for btn in [save_button, load_button]:
            btn.setFixedWidth(150)
            btn.setStyleSheet(calculate_button.styleSheet())


        # ⚠️ Uyarı kutusu - tek QLabel içinde ikon + metin
        warning_label = QLabel("⚠️  Do not perform operations here before generating the table in the Prerace Stint Calculator tab!")
        warning_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #c0392b;
                font-size: 13px;
                padding: 10px 12px;
                border: 1px solid #e74c3c;
                border-radius: 6px;
                font-family: Poppins;
                font-weight: bold;
            }
        """)
        warning_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # → Buton + Uyarı yan yana
        calculate_row.addWidget(calculate_button)
        calculate_row.addWidget(save_button)
        calculate_row.addWidget(load_button)
        calculate_row.addWidget(warning_label)  # ← eski warning_widget yerine
        calculate_row.setSpacing(16)
        layout.addLayout(calculate_row)

        # ✅ Buton fonksiyon bağlantıları
        class_name = "hypercar"
        car_name = "alpinea424"
        track_name = "silverstonecircuit"

        save_button.clicked.connect(lambda: self.save_inputs_to_json(class_name, car_name, track_name))
        load_button.clicked.connect(lambda: self.load_inputs_from_json(class_name, car_name, track_name))

        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(4)
        self.table.setColumnWidth(0, 80)   # Stint No
        self.table.setColumnWidth(1, 340)  # Strategy
        self.table.setColumnWidth(2, 800)  # Start - Finish
        self.table.setColumnWidth(3, 200)  # Driver

        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30, 242))  # 0.95 opaklık
        self.table.setPalette(palette)

        # ✅ Viewport için doğrudan stil uygula (en kritik satır)
        self.table.viewport().setStyleSheet("""
            background-color: rgba(30, 30, 30, 0.95);
        """)

        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView {
                background: rgba(30, 30, 30, 0.95);
            }
            QHeaderView::section {
                background-color: rgba(30, 30, 30, 0.95);
                color: #ffd700;
                font-weight: bold;
                font-size: 14px;
                padding: 6px;
                border: none;
            }
        """)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 30, 30, 0.95);
                alternate-background-color: rgba(50, 50, 50, 0.9);
                color: white;
                font-size: 14px;
                font-family: Poppins;
                border: none;
                gridline-color: transparent;
            }

            QTableWidget::item {
                background-color: transparent;
            }

            QTableWidget QHeaderView::section {
                background-color: transparent;
                color: #ffd700;
                font-weight: bold;
                font-size: 14px;
                padding: 6px;
                border: none;
            }

            QHeaderView::section {
                background-color: transparent;
                color: #ffd700;
                font-weight: bold;
                font-size: 14px;
                padding: 6px;
                border: none;
            }

            QTableCornerButton::section {
                background-color: rgba(30, 30, 30, 0.95);
                border: none;
            }

            QScrollBar:vertical, QScrollBar:horizontal {
                background: rgba(30, 30, 30, 0.5);
            }

            QScrollBar::handle {
                background: #ffd700;
                border-radius: 4px;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                border: none;
            }
        """)

        self.table.setColumnCount(4)
        self.table.setColumnWidth(1, 360)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 250)
        self.table.setMaximumWidth(1000)
        self.table.verticalHeader().setDefaultSectionSize(230)
        self.table.setHorizontalHeaderLabels(["Stint No", "Strategy", "Start - Finish", "Driver"])

        self.table.setRowCount(10)
        for row in range(10):
            self.table.setItem(row, 0, QTableWidgetItem(f"Stint {row + 1}"))
            self.table.setCellWidget(row, 3, QComboBox())

        # 🔶 Sağdaki driver summary tablosu
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(3)
        self.summary_table.setHorizontalHeaderLabels(["Driver", "Total Time", "Total %"])
        self.summary_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 30, 30, 0.95);
                color: white;
                font-size: 14px;
                font-family: Poppins;
                border: none;
            }

            QHeaderView {
                background-color: transparent;
            }

            QTableWidget QHeaderView::section {
                background-color: rgba(30, 30, 30, 0.95);
                color: #ffd700;
                font-weight: bold;
                font-size: 14px;
                padding: 6px;
                border: none;
            }

            QTableCornerButton::section {
                background-color: transparent;
                border: none;
            }
        """)
        self.summary_table.verticalHeader().setVisible(False)
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.summary_table.setFixedWidth(700)
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Driver sütunu genişlesin
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        table_row = QHBoxLayout()
        table_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        table_row.addWidget(self.table)
        table_row.addWidget(self.summary_table)
        layout.addLayout(table_row)


    def on_strategy_changed(self):
        btn = self.radio_group.checkedButton()
        if btn:
            self.selected_strategy = btn.text().lower().replace(" ", "_")

            if self.strategy_selected_callback:
                widgets = self.get_cloned_strategy_widgets(self.selected_strategy)
                self.strategy_selected_callback(widgets)

    def load_inputs_from_json(self, class_name, car_name, track_name):
        key = f"{class_name.lower()}_{car_name.lower()}_{track_name.lower()}".replace(" ", "")
        filename = os.path.join("data", "strategy_inputs", f"{key}.json")

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            # ✅ start_time varsa doğrudan QDateTime olarak ayarla
            if "start_time" in data:
                try:
                    start_dt = QDateTime.fromString(data["start_time"], "dd MMM yyyy HH:mm")
                    if start_dt.isValid():
                        self.race_start_picker.setDateTime(start_dt)
                except Exception as e:
                    print("RST yüklenemedi:", e)

            # ✅ Eğer driver_assignments varsa ComboBox’lara set et
            if "driver_assignments" in data:
                assignments = data["driver_assignments"]
                for row, driver in assignments.items():
                    try:
                        combo = self.table.cellWidget(int(row), 3)  # Sütun 3: Driver
                        if isinstance(combo, QComboBox):
                            combo.setCurrentText(driver)
                    except Exception as e:
                        print(f"Driver yukleme hatasi (row={row}): {e}")

            print(">>> JSON yüklendi:", data)
        else:
            print(">>> Dosya bulunamadı:", filename)


    def copy_strategy_widgets_direct(self, strategy_name):
        index_map = {
            "strategy_a": 2,
            "strategy_b": 3,
            "strategy_c": 4,
            "strategy_d": 5
        }
        col_index = index_map.get(strategy_name)
        if col_index is None:
            return

        previous_drivers = {}
        manual_times = {}
        manual_flags = {}
        self.setFocus()

        for i in range(self.table.rowCount()):
            combo = self.table.cellWidget(i, 3)
            if combo:
                previous_drivers[i] = combo.currentText()

            time_widget = self.table.cellWidget(i, 2)
            if isinstance(time_widget, StintTimeWidget):
                manual_times[i] = time_widget.get_times()
                manual_flags[i] = time_widget.is_manual()


        row_count = self.table_component.table.rowCount()
        self.table.setRowCount(row_count)

        global_start_time = self.race_start_picker.dateTime().toSecsSinceEpoch()
        current_time = global_start_time

        for i in range(row_count):
            self.table.setItem(i, 0, QTableWidgetItem(f"Stint {i + 1}"))

            original_widget = self.table_component.table.cellWidget(i, col_index)
            if original_widget is None:
                continue

            # --- STRATEGY KART KLONU ---
            cloned_widget = original_widget.__class__()
            cloned_widget.setFixedWidth(360)
            cloned_widget.setFixedHeight(220)
            cloned_layout = QVBoxLayout(cloned_widget)
            cloned_layout.setSpacing(15)
            fuel_virtual_row = QHBoxLayout()

            for child in original_widget.findChildren(QLabel):
                label_text = child.text()
                copy_label = QLabel(label_text)
                copy_label.setStyleSheet(child.styleSheet())
                copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                copy_label.setFixedHeight(child.height())

                if "Fuel" in label_text or "Virtual" in label_text:
                    fuel_virtual_row.addWidget(copy_label)
                else:
                    cloned_layout.addWidget(copy_label)
            cloned_layout.addLayout(fuel_virtual_row)
            self.table.setCellWidget(i, 1, cloned_widget)

            # --- STINT + PIT SÜRESİ ---
            stint_seconds = 0
            pit_seconds = 0
            for lbl in original_widget.findChildren(QLabel):
                txt = lbl.text()
                if "Stint Time" in txt:
                    try:
                        t = txt.split(": ", 1)[-1]
                        h, m, s = map(int, t.strip().split(":"))
                        stint_seconds = h * 3600 + m * 60 + s
                    except:
                        pass
                elif "Pit Time" in txt:
                    try:
                        t = txt.split(": ", 1)[-1]
                        h, m, s = map(int, t.strip().split(":"))
                        pit_seconds = h * 3600 + m * 60 + s
                    except:
                        pass
            total_seconds = stint_seconds + pit_seconds

            # --- SAAT HESAPLAMA ---
            if i in manual_flags and manual_flags[i]:  # sadece checkbox işaretliyse işle
                manual_start, manual_finish = manual_times.get(i, ("", ""))

                # START
                if manual_start.strip():
                    start_str = manual_start.strip()
                    start_qt = QTime.fromString(start_str, "HH:mm")
                    if start_qt.isValid():
                        date = self.race_start_picker.dateTime().date()
                        start_dt = QDateTime(date, start_qt)
                        current_time = start_dt.toSecsSinceEpoch()
                    else:
                        start_str = QDateTime.fromSecsSinceEpoch(int(current_time)).toString("HH:mm")
                else:
                    start_str = QDateTime.fromSecsSinceEpoch(int(current_time)).toString("HH:mm")

                # FINISH
                if manual_finish.strip():
                    finish_str = manual_finish.strip()
                    finish_qt = QTime.fromString(finish_str, "HH:mm")
                    if finish_qt.isValid():
                        date = self.race_start_picker.dateTime().date()
                        finish_dt = QDateTime(date, finish_qt)
                        current_time = finish_dt.toSecsSinceEpoch()
                else:
                    finish_time = current_time + total_seconds
                    finish_str = QDateTime.fromSecsSinceEpoch(int(finish_time)).toString("HH:mm")
                    current_time = finish_time

            else:
                start_str = QDateTime.fromSecsSinceEpoch(int(current_time)).toString("HH:mm")
                finish_time = current_time + total_seconds
                finish_str = QDateTime.fromSecsSinceEpoch(int(finish_time)).toString("HH:mm")
                current_time = finish_time


                # --- ZAMAN WIDGET'I EKLE ---
                time_widget = StintTimeWidget(start_str, finish_str, editable=False)
                self.table.setCellWidget(i, 2, time_widget)

            # --- DRIVER ---
            combo = QComboBox()
            combo.addItem("-")
            combo.addItems(self.pilot_list)
            if i in previous_drivers:
                combo.setCurrentText(previous_drivers[i])

            strategy_widget = self.table.cellWidget(i, 1)
            is_disabled = False
            if strategy_widget is None or strategy_widget.findChild(QLabel) is None:
                is_disabled = True
            else:
                texts = [lbl.text().strip() for lbl in strategy_widget.findChildren(QLabel)]
                if all(t == "" or t == "-" for t in texts):
                    is_disabled = True

            combo.setEnabled(not is_disabled)
            combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {"#2a2a2a" if is_disabled else "rgba(255, 215, 0, 0.4)"};
                    color: {"#555555" if is_disabled else "white"};
                    border: none;
                    padding: 6px;
                    border-radius: 4px;
                    font-family: Poppins;
                }}
                QComboBox QAbstractItemView {{
                    background-color: rgba(30, 30, 30, 0.25);
                    color: white;
                    selection-background-color: #ffd700;
                }}
            """)
            self.table.setCellWidget(i, 3, combo)


    def set_table_component(self, table_component):
        self.table_component = table_component

    def save_inputs_to_json(self, class_name, car_name, track_name):
        key = f"{class_name.lower()}_{car_name.lower()}_{track_name.lower()}".replace(" ", "")
        filename = os.path.join("data", "strategy_inputs", f"{key}.json")

        # 🔁 JSON'u tek seferde oku
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                print(">>> JSON okunamadı, boş başlatıldı.")
                data = {}
        else:
            data = {}

        # ✅ Güncellemeler
        data["start_time"] = self.race_start_picker.dateTime().toString("dd MMM yyyy HH:mm")
        data["team"] = self.team_selector.currentText()
        data["loadstrategy"] = self.selected_strategy

        # 🔁 race_time korunuyorsa elleme, sadece varsa yeniden yaz
        if "race_time" not in data:
            data["race_time"] = "00:00:00"

        # ✅ QComboBox'lardan pilot seçimlerini al
        assignments = {}
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 3)
            if isinstance(combo, QComboBox):
                selected_driver = combo.currentText().strip()
                if selected_driver and selected_driver != "-":
                    assignments[str(row)] = selected_driver

        data["driver_assignments"] = assignments

        # 🔁 Dosyaya kaydet
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(">>> JSON güncellendi:", filename)



    def on_calculate_clicked(self):
        # 🔍 Ön kontrol: sadece finish girilmiş ama zincir start girilmemişse uyar
        for i in range(self.table.rowCount() - 1):  # sondaki satırda kontrol gerekmez
            time_widget = self.table.cellWidget(i, 2)
            next_time_widget = self.table.cellWidget(i + 1, 2)

            if not time_widget or not next_time_widget:
                continue

            labels = time_widget.findChildren(QLineEdit)
            next_labels = next_time_widget.findChildren(QLineEdit)

            if len(labels) == 2 and len(next_labels) == 2:
                finish = labels[1].text().strip()
                next_start = next_labels[0].text().strip()

                if finish and not next_start:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self,
                        "Eksik Giriş",
                        f"Stint {i + 1} için bir bitiş saati girmişsiniz.\n"
                        f"Lütfen Stint {i + 2} için başlangıç saati de girin."
                    )
                    return  # Hesaplamayı durdur

        # ↩️ Normal akış devam etsin
        selected_team = self.team_selector.currentText()
        class_name = "hypercar"
        car_name = "alpinea424"
        track_name = "silverstonecircuit"

        self.copy_strategy_widgets_direct(self.selected_strategy)
        self.update_driver_summary_table()



    def set_current_team(self, team_name):
        self.team_name = team_name
        filepath = f"data/teams_drivers/{team_name}.json"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.driver_list = [d for d in data.get("drivers", []) if d.strip()]
                self.pilot_list = self.driver_list

                # ✅ Her pilota sırayla renk ata (dinamik)
                base_colors = ["#FFD700", "#00BFFF", "#32CD32", "#FF8C00", "#BA55D3", "#DC143C"]
                self.driver_colors = {
                    driver: base_colors[i % len(base_colors)]
                    for i, driver in enumerate(self.pilot_list)
                }

                self.populate_driver_dropdowns()

    def populate_driver_dropdowns(self):
        if not hasattr(self, "table"):
            return  # tablo henüz yoksa boş geç

        row_count = self.table.rowCount()
        for row in range(row_count):
            combo = QComboBox()
            combo.addItem("-")
            combo.addItems(self.driver_list)

            # ✅ Varsayılan pilot ve renk belirleme
            driver_name = combo.currentText().strip()
            bg_color = self.driver_colors.get(driver_name, "#2a2a2a")

            # ✅ Stil uygula
            combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {bg_color};
                    color: white;
                    border: none;
                    padding: 6px;
                    border-radius: 4px;
                    font-family: Poppins;
                }}
                QComboBox QAbstractItemView {{
                    background-color: rgba(30, 30, 30, 0.95);
                    color: white;
                    selection-background-color: #FFD700;
                }}
            """)

            # ✅ Seçim değişirse arka plan güncelle
            combo.currentTextChanged.connect(lambda _, row=row, combo=combo: self.update_driver_style(row, combo))

            self.table.setCellWidget(row, 3, combo)

    def update_driver_style(self, row, combo):
        driver = combo.currentText().strip()
        bg_color = self.driver_colors.get(driver, "#2a2a2a")
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 6px;
                border-radius: 4px;
                font-family: Poppins;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(30, 30, 30, 0.95);
                color: white;
                selection-background-color: #FFD700;
            }}
        """)

    def load_teams_to_dropdown(self):
        self.team_selector.clear()
        folder = "data/teams_drivers"
        if os.path.exists(folder):
            for file in sorted(os.listdir(folder)):
                if file.endswith(".json"):
                    team = file.replace(".json", "")
                    self.team_selector.addItem(team)

    def update_driver_summary_table(self):
        from collections import defaultdict

        driver_times = defaultdict(int)
        total_race_seconds = 0

        row_count = self.table.rowCount()

        for row in range(row_count):
            driver_combo = self.table.cellWidget(row, 3)
            if not driver_combo:
                continue
            driver = driver_combo.currentText().strip()
            if driver == "-" or not driver:
                continue  # boş seçimleri atla

            # Strategy hücresi kontrolü (zorunlu değil ama varsa korunabilir)
            strategy_widget = self.table.cellWidget(row, 1)
            if not strategy_widget:
                continue

            # 🔄 Start-Finish saat farkından süreyi hesapla
            time_widget = self.table.cellWidget(row, 2)
            if time_widget:
                if isinstance(time_widget, StintTimeWidget):
                    start_str, finish_str = time_widget.get_times()
                    start_time = QTime.fromString(start_str, "HH:mm")
                    finish_time = QTime.fromString(finish_str, "HH:mm")
                    if start_time.isValid() and finish_time.isValid():
                        total = start_time.secsTo(finish_time)
                        if total < 0:
                            total += 24 * 3600  # gece yarısı aşımı için düzeltme
                    else:
                        total = 0
                else:
                    total = 0
            else:
                total = 0

            # 🔢 Toplam süreyi topla
            total_race_seconds += total
            driver_times[driver] += total

        # tabloyu doldur
        self.summary_table.setRowCount(len(driver_times))

        for i, (driver, total_sec) in enumerate(driver_times.items()):
            time_str = QTime(0, 0).addSecs(total_sec).toString("hh:mm:ss")
            percent = (total_sec / total_race_seconds * 100) if total_race_seconds > 0 else 0

            # 🎯 Hücreler
            item_driver = QTableWidgetItem(driver)
            item_time = QTableWidgetItem(time_str)
            item_percent = QTableWidgetItem(f"{percent:.1f}%")

            # 🎯 Font büyütme
            font = item_driver.font()
            font.setPointSize(16)
            item_driver.setFont(font)
            item_time.setFont(font)
            item_percent.setFont(font)

            # 🔴 %70 ve üzeri için arka plan kırmızı
            if percent >= 70.0:
                item_percent.setBackground(QBrush(QColor("#e74c3c")))
                item_percent.setForeground(QBrush(Qt.GlobalColor.white))

            # 📌 Tabloya eklemeden önce her şey hazır
            self.summary_table.setItem(i, 0, item_driver)
            self.summary_table.setItem(i, 1, item_time)

            # 🎯 Total % hücresi QLabel ile (garanti stil)
            label_percent = QLabel(f"{percent:.1f}%")
            label_percent.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_percent.setStyleSheet(f"""
                background-color: {"#e74c3c" if percent >= 70 else "transparent"};
                color: {"white" if percent >= 70 else "white"};
                font-size: 16px;
                font-weight: bold;
                font-family: Poppins;
                padding: 6px;
                border-radius: 4px;
            """)

            self.summary_table.setCellWidget(i, 2, label_percent)

    def get_cloned_strategy_widgets(self, strategy_name: str):
        index_map = {
            "strategy_a": 2,
            "strategy_b": 3,
            "strategy_c": 4,
            "strategy_d": 5
        }
        col_index = index_map.get(strategy_name)
        if col_index is None or not hasattr(self, "table_component"):
            return []

        widgets = []
        row_count = self.table_component.table.rowCount()

        for i in range(row_count):
            original_widget = self.table_component.table.cellWidget(i, col_index)
            if original_widget is None:
                continue

            # yeni widget
            cloned_widget = QWidget()
            layout = QVBoxLayout(cloned_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            fuel_virtual_row = QHBoxLayout()

            for child in original_widget.findChildren(QLabel):
                lbl = QLabel(child.text())
                lbl.setStyleSheet(child.styleSheet())
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if "Fuel" in child.text() or "Virtual" in child.text():
                    fuel_virtual_row.addWidget(lbl)
                else:
                    layout.addWidget(lbl)

            layout.addLayout(fuel_virtual_row)
            widgets.append(cloned_widget)

        return widgets

class StintTimeWidget(QWidget):
    def __init__(self, start_text="", finish_text="", editable=False):
        super().__init__()

        self.start_input = QLineEdit(start_text)
        self.finish_input = QLineEdit(finish_text)
        self.start_input.setStyleSheet("""
            QLineEdit {
                background-color: #2ecc71;  /* Yeşil */
                color: white;
                font-weight: bold;
                border: 1px solid #27ae60;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: Poppins;
            }
        """)
        self.finish_input.setStyleSheet("""
            QLineEdit {
                background-color: #e74c3c;  /* Kırmızı */
                color: white;
                font-weight: bold;
                border: 1px solid #c0392b;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: Poppins;
            }
        """)

        for input in (self.start_input, self.finish_input):
            input.setFixedWidth(60)
            input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input.setStyleSheet("""
                QLineEdit {
                    background-color: #222;
                    color: white;
                    font-weight: bold;
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 4px;
                    font-family: Poppins;
                }
            """)

        self.checkbox = QCheckBox("🖊️")
        self.checkbox.setChecked(editable)
        self.checkbox.setToolTip("Manuel saat girişi")
        self.checkbox.stateChanged.connect(self.toggle_editable)

        self.toggle_editable()

        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("Start:"))
        row.addWidget(self.start_input)
        row.addWidget(QLabel("Finish:"))
        row.addWidget(self.finish_input)
        layout.addLayout(row)
        layout.addWidget(self.checkbox)

        self.setLayout(layout)
        self.setStyleSheet("color: white;")

    def toggle_editable(self):
        editable = self.checkbox.isChecked()
        self.start_input.setReadOnly(not editable)
        self.finish_input.setReadOnly(not editable)

        self.start_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                border: 1px solid #27ae60;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: Poppins;
            }}
        """)
        self.finish_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border: 1px solid #c0392b;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: Poppins;
            }}
        """)

    def get_times(self):
        return self.start_input.text().strip(), self.finish_input.text().strip()

    def is_manual(self):
        return self.checkbox.isChecked()



