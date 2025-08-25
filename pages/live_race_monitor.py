# pages/live_race_monitor.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QRadioButton, QButtonGroup, QPushButton, QComboBox, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QDateTime, QTime, QDate, QLocale
from pages.table_component import TableComponent
from pages.strategy_utils import generate_adaptive_strategies
import re  # ⏱ süre metni için
#from pages.strategy_utils import generate_strategy_table

def parse_average_lap_time(text: str) -> int:
    try:
        minutes, rest = text.strip().split(":")
        seconds = float(rest)
        return int(int(minutes) * 60 + seconds)
    except Exception as e:
        print(f"❌ parse_average_lap_time() hatası: {e}")
        return 90  # fallback değeri

class LiveRaceMonitor(QWidget):
    def __init__(self):
        super().__init__()

        self.fcy_timer = QTimer(self)
        self.fcy_timer.timeout.connect(self.update_fcy_timer)

        self.pitlane_timer = QTimer(self)
        self.pitlane_timer.timeout.connect(self.update_pitlane_timer)

        self.pitzone_timer = QTimer(self)
        self.pitzone_timer.timeout.connect(self.update_pitzone_timer)

        self.adaptive_strategy_widget = QWidget()
        self.adaptive_strategy_widget.setVisible(False)
        self.adaptive_strategy_layout = QVBoxLayout(self.adaptive_strategy_widget)

        # ⛽ Pitlane timer özel kontrolü
        self.pitlane_pause_time = None

        self.fcy_timer_start = None
        self.pitlane_timer_start = None
        self.pitzone_timer_start = None

        self.fcy_time_label = QLabel("⏱ FCY: 00:00")
        self.pitlane_time_label = QLabel("⏱ Pitlane: 00:00")
        self.pitzone_time_label = QLabel("⏱ Pitzone: 00:00")

        self.fcy_snapshot_label = QLabel("🕒 FCY Start: --:--:--\n🕒 FCY Finish: --:--:--")

        self.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 2, 30, 2)
        layout.setSpacing(20)

        # Zamanlayıcılar
        self.finish_timer = QTimer(self)
        self.finish_timer.timeout.connect(self.update_finish_timer)
        self.finish_time_left = 0
        self.finish_timer_running = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.target_time = QDateTime.currentDateTime().addSecs(3600)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_strategy_preview)
        self.refresh_timer.start(60000)

        self.countdown_label = QLabel("--:--:--")
        self.finish_countdown = QLabel("--:--:--")
        self.finish_start_pause_button = QPushButton("▶")
        self.finish_start_pause_button.clicked.connect(self.toggle_finish_timer)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Strategy A", "Strategy B", "Strategy C", "Strategy D"])
        self.strategy_combo.currentIndexChanged.connect(self.on_strategy_changed)

        self.refresh_button = QPushButton("Refresh Strategy")
        self.refresh_button.clicked.connect(self.refresh_strategy_preview)

        # 🔳 Üst Satır – Strategy Zone + Countdownlar
        top_row = QWidget()
        top_row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(4)
        top_row_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.strategy_zone = QWidget()
        self.strategy_zone.setMinimumHeight(120)
        self.strategy_zone.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.strategy_zone.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.25);
            border-radius: 10px;
        """)
        self.strategy_zone_layout = QVBoxLayout(self.strategy_zone)
        self.strategy_zone_layout.setContentsMargins(12, 12, 12, 12)
        self.strategy_zone_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        strategy_row = QWidget()
        strategy_row_layout = QHBoxLayout(strategy_row)
        strategy_row_layout.setContentsMargins(0, 0, 0, 0)
        strategy_row_layout.setSpacing(12)

        strategy_label = QLabel("🎯 Select Strategy:")
        strategy_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            font-family: Poppins;
        """)

        self.strategy_combo.setFixedWidth(160)
        self.strategy_combo.setStyleSheet("""
            QComboBox {
                background-color: black;
                color: white;
                padding: 8px 16px;
                font-family: Poppins;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: black;
                color: white;
                selection-background-color: #FFD700;
            }
        """)

        self.refresh_button.setFixedWidth(160)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                font-weight: bold;
                font-size: 14px;
                font-family: Poppins;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #ffcc00;
            }
        """)


        strategy_row_layout.addWidget(strategy_label)
        strategy_row_layout.addWidget(self.strategy_combo)
        strategy_row_layout.addWidget(self.refresh_button)

        #strategy_row_layout.addWidget(fcy_strategy_label)
        #strategy_row_layout.addWidget(self.fcy_base_strategy_combo)

        strategy_row_layout.addStretch()
        self.strategy_zone_layout.addWidget(strategy_row)

        start_card = QWidget()
        start_card.setFixedSize(240, 120)
        start_card.setStyleSheet("background-color: rgba(0, 0, 0, 0.25); border-radius: 12px;")
        start_layout = QVBoxLayout(start_card)
        start_layout.setContentsMargins(12, 12, 12, 12)
        start_layout.setSpacing(8)

        start_title = QLabel("⏳ Race Start Countdown")
        start_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        start_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px; font-family: Poppins;")

        self.countdown_label.setFixedSize(180, 40)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            background-color: #FFD700;
            color: black;
            font-weight: bold;
            font-size: 18px;
            border-radius: 8px;
            font-family: Poppins;
        """)

        start_layout.addWidget(start_title)
        start_layout.addWidget(self.countdown_label)

        finish_card = QWidget()
        finish_card.setFixedSize(240, 120)
        finish_card.setStyleSheet("background-color: rgba(0, 0, 0, 0.25); border-radius: 12px;")
        finish_layout = QVBoxLayout(finish_card)
        finish_layout.setContentsMargins(12, 12, 12, 12)
        finish_layout.setSpacing(8)

        finish_title = QLabel("⏱ Race Finish Countdown")
        finish_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        finish_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px; font-family: Poppins;")

        self.finish_countdown.setFixedSize(140, 40)
        self.finish_countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.finish_countdown.setStyleSheet("""
            background-color: #FFD700;
            color: black;
            font-weight: bold;
            font-size: 18px;
            border-radius: 8px;
            font-family: Poppins;
        """)

        self.finish_start_pause_button.setFixedSize(40, 40)
        self.finish_start_pause_button.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #FFD700;
                font-weight: bold;
                font-size: 16px;
                border-radius: 6px;
            }
        """)

        finish_row = QWidget()
        finish_row_layout = QHBoxLayout(finish_row)
        finish_row_layout.setContentsMargins(0, 0, 0, 0)
        finish_row_layout.setSpacing(8)
        finish_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        finish_row_layout.addWidget(self.finish_countdown)
        finish_row_layout.addWidget(self.finish_start_pause_button)

        finish_layout.addWidget(finish_title)
        finish_layout.addWidget(finish_row)

        top_row_layout.addWidget(self.strategy_zone)
        top_row_layout.addWidget(start_card)
        top_row_layout.addWidget(finish_card)
        layout.addWidget(top_row)

        # 🔻 Strategy Preview Zone – Alt alan
        self.strategy_preview_zone = QWidget()
        self.strategy_preview_zone.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.25);
            border-radius: 10px;
        """)
        self.strategy_preview_zone_layout = QVBoxLayout(self.strategy_preview_zone)
        self.strategy_preview_zone_layout.setContentsMargins(12, 12, 12, 12)
        self.strategy_preview_zone_layout.setSpacing(16)
        self.strategy_preview_zone_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 🧱 Scrollable Stint Tablosu Alanı
        stint_table_frame = QWidget()
        stint_table_frame.setFixedWidth(330)
        stint_table_layout = QVBoxLayout(stint_table_frame)
        stint_table_layout.setContentsMargins(0, 0, 0, 0)
        stint_table_layout.setSpacing(0)

        self.strategy_table_container = QWidget()
        self.strategy_table_container.setFixedWidth(308)
        self.strategy_table_container.setStyleSheet("background-color: transparent;")

        self.strategy_table_layout = QVBoxLayout(self.strategy_table_container)
        self.strategy_table_layout.setContentsMargins(0, 0, 0, 0)
        self.strategy_table_layout.setSpacing(12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setFixedWidth(320)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QScrollBar:vertical {
                width: 12px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        scroll_area.setWidget(self.strategy_table_container)

        stint_table_layout.addWidget(scroll_area)

        # 🟡 FCY Panel
        self.fcy_time_label = QLabel("⏱ FCY: 00:00")
        self.pitlane_time_label = QLabel("⏱ Pitlane: 00:00")
        self.pitzone_time_label = QLabel("⏱ Pitzone: 00:00")
        self.fcy_snapshot_label = QLabel("🕒 FCY Start: --:--:--\n🕒 FCY Finish: --:--:--")

        self.fcy_start_button = QPushButton("▶ FCY")
        self.fcy_start_button.clicked.connect(self.toggle_fcy_timer)

        fcy_widget = QWidget()
        fcy_widget.setFixedWidth(320)
        fcy_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.3); border-radius: 10px;")
        fcy_layout = QVBoxLayout(fcy_widget)
        fcy_layout.setContentsMargins(12, 12, 12, 12)
        fcy_layout.setSpacing(8)

        title = QLabel("🟡 FCY Panel")
        title.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 16px; font-family: Poppins;")

        self.fcy_time_label.setStyleSheet("color: white; font-size: 14px; font-family: Poppins;")
        self.pitlane_time_label.setStyleSheet("color: white; font-size: 14px; font-family: Poppins;")
        self.pitzone_time_label.setStyleSheet("color: white; font-size: 14px; font-family: Poppins;")
        self.fcy_snapshot_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            background-color: rgba(0, 0, 0, 0.3);
            padding: 6px;
            border-radius: 6px;
            font-family: Poppins;
        """)
        self.fcy_start_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                padding: 6px;
                font-family: Poppins;
            }
        """)

        fcy_layout.addWidget(title)
        fcy_layout.addWidget(self.fcy_time_label)
        fcy_layout.addWidget(self.pitlane_time_label)
        fcy_layout.addWidget(self.pitzone_time_label)
        fcy_layout.addWidget(self.fcy_snapshot_label)
        fcy_layout.addWidget(self.fcy_start_button)

        # 🔘 Pitlane Butonları
        pitlane_btns = QWidget()
        pitlane_btns_layout = QHBoxLayout(pitlane_btns)
        pitlane_btns_layout.setContentsMargins(0, 0, 0, 0)
        pitlane_btns_layout.setSpacing(8)

        pitlane_start_btn = QPushButton("▶ Pitlane In")
        pitlane_stop_btn = QPushButton("⏹ Pitlane Out")

        pitlane_start_btn.clicked.connect(lambda: self.start_timer("pitlane"))
        pitlane_stop_btn.clicked.connect(lambda: self.stop_timer("pitlane"))

        pitlane_start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
                font-family: Poppins;
            }
        """)
        pitlane_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
                font-family: Poppins;
            }
        """)

        pitlane_btns_layout.addWidget(pitlane_start_btn)
        pitlane_btns_layout.addWidget(pitlane_stop_btn)
        fcy_layout.addWidget(pitlane_btns)

        # 🔘 Pitzone Butonları (Aynı zamanda Pitlane'i duraklat/devam ettirir)
        pitzone_btns = QWidget()
        pitzone_btns_layout = QHBoxLayout(pitzone_btns)
        pitzone_btns_layout.setContentsMargins(0, 0, 0, 0)
        pitzone_btns_layout.setSpacing(8)

        pitzone_start_btn = QPushButton("▶ Pitzone In")
        pitzone_stop_btn = QPushButton("⏹ Pitzone Out")

        pitzone_start_btn.clicked.connect(lambda: (self.stop_timer("pitlane"), self.start_timer("pitzone")))
        pitzone_stop_btn.clicked.connect(lambda: (self.stop_timer("pitzone"), self.start_timer("pitlane")))

        pitzone_start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
                font-family: Poppins;
            }
        """)
        pitzone_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 6px;
                font-family: Poppins;
            }
        """)

        pitzone_btns_layout.addWidget(pitzone_start_btn)
        pitzone_btns_layout.addWidget(pitzone_stop_btn)
        fcy_layout.addWidget(pitzone_btns)

        horizontal_container = QHBoxLayout()
        horizontal_container.setContentsMargins(0, 0, 0, 0)
        horizontal_container.setSpacing(16)
        horizontal_container.addWidget(stint_table_frame)
        horizontal_container.addWidget(fcy_widget)
        horizontal_container.addWidget(self.adaptive_strategy_widget)

        self.strategy_preview_zone_layout.addLayout(horizontal_container)
        layout.addWidget(self.strategy_preview_zone)

        # 📦 Scrollable FCY preview alanı
        scroll_fcy_preview = QScrollArea()
        scroll_fcy_preview.setWidgetResizable(True)
        scroll_fcy_preview.setFixedWidth(320)
        scroll_fcy_preview.setFixedHeight(660)  # Yukarıdan/aşağıdan kesilmemesi için sınır veriyoruz
        scroll_fcy_preview.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 10px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #FFD700;
                border-radius: 5px;
                min-height: 20px;
            }
        """)

        # 👉 FCY preview hücrelerinin bulunduğu konteyner (scroll içine gömülür)
        self.fcy_preview_container = QWidget()
        self.fcy_preview_container.setStyleSheet("background-color: transparent;")
        self.fcy_preview_layout = QVBoxLayout(self.fcy_preview_container)
        self.fcy_preview_layout.setContentsMargins(0, 0, 0, 0)
        self.fcy_preview_layout.setSpacing(12)

        scroll_fcy_preview.setWidget(self.fcy_preview_container)

        # 🧠 FCY Strategy Preview Başlığı
        fcy_preview_title = QLabel("🧠 FCY Strategy Preview")
        fcy_preview_title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        fcy_preview_title.setFixedHeight(66)  # Sarı kartlarla uyumlu
        fcy_preview_title.setFixedWidth(308)  # じ FCY kartlarıyla hizalı
        fcy_preview_title.setContentsMargins(12, 0, 0, 0)  # Soldan içerik boşluğu
        fcy_preview_title.setStyleSheet("""
            background-color: #FFD700;
            color: black;
            font-size: 14px;
            font-weight: bold;
            font-family: Poppins;
            border-radius: 8px;
        """)

        self.adaptive_strategy_layout.addWidget(fcy_preview_title)

        self.adaptive_strategy_layout.addWidget(scroll_fcy_preview)

        weather_label = QLabel("☁️ Weather Forecast Placeholder")
        weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weather_label.setStyleSheet("color: lightblue; font-size: 18px; font-weight: bold;")
        layout.addWidget(weather_label)

        radar_label = QLabel("📡 Radar Image Placeholder")
        radar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        radar_label.setStyleSheet("color: lightgreen; font-size: 18px; font-weight: bold;")
        layout.addWidget(radar_label)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_strategy_preview)
        self.refresh_timer.start(60000)


    def load_selected_strategy(self, widgets: list[QWidget], driver_names: list[str]):
        """
        DriversTimePage'den gelen görsel widget listesini strateji önizleme alanına yansıtır.
        Her widget için başlık (Stint X) sarmalayıcıya eklenir.
        Ayrıca her başlığın altına ilgili sürücünün adı da eklenir.
        """
        if hasattr(self, "strategy_table_layout"):
            # Eski widget'ları temizle
            while self.strategy_table_layout.count():
                item = self.strategy_table_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # 🟡 Sürücü isimlerini al
            driver_names = []
            main_window = self.window()
            if hasattr(main_window, "page_drivers_time"):
                page = main_window.page_drivers_time
                for i in range(len(widgets)):
                    combo = page.table.cellWidget(i, 3)
                    if isinstance(combo, QComboBox):
                        driver_names.append(combo.currentText().strip())
                    else:
                        driver_names.append("")

            # Yeni widget'ları ekle
            for i, w in enumerate(widgets):
                wrapper = QWidget()
                wrapper_layout = QVBoxLayout(wrapper)
                wrapper.setContentsMargins(0, 0, 0, 0)
                wrapper_layout.setSpacing(6)
                wrapper.setFixedWidth(300)

                stint_label = QLabel(f"Stint {i + 1}")
                stint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                stint_label.setFixedWidth(300)
                stint_label.setStyleSheet("""
                    color: white;
                    background-color: rgba(0, 0, 0, 0.5);
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px;
                """)

                driver_label = QLabel(driver_names[i] if i < len(driver_names) else "-")
                driver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                driver_label.setFixedWidth(300)
                driver_label.setStyleSheet("""
                    color: #FFD700;
                    font-size: 13px;
                    font-style: italic;
                    padding-bottom: 2px;
                """)

                wrapper_layout.addWidget(stint_label)
                wrapper_layout.addWidget(driver_label)
                w.setFixedWidth(300)
                wrapper_layout.addWidget(w)

                self.strategy_table_layout.addWidget(wrapper)

    def update_timer(self):
        now = QDateTime.currentDateTime().toLocalTime()
        secs_left = now.secsTo(self.target_time)

        if secs_left <= 0:
            countdown_str = "Race Started!"
        else:
            days = secs_left // 86400
            hours = (secs_left % 86400) // 3600
            minutes = (secs_left % 3600) // 60
            seconds = secs_left % 60

            time_parts = []
            if days > 0:
                time_parts.append(f"{days}D")
            if hours > 0:
                time_parts.append(f"{hours}H")
            if minutes > 0:
                time_parts.append(f"{minutes}M")
            if seconds > 0:
                time_parts.append(f"{seconds}S")
            if not time_parts:
                time_parts.append("<1S")

            countdown_str = " ".join(time_parts)

        self.countdown_label.setText(countdown_str)

    def set_target_time(self, qdatetime: QDateTime):
        now = QDateTime.currentDateTime().toLocalTime()
        if qdatetime and qdatetime.isValid():
            self.target_time = qdatetime.toLocalTime()
        else:
            print("❌ Geçersiz QDateTime geldi:", qdatetime)

    def show_strategy_preview_widgets(self, widgets: list[QWidget]):
        """
        DriversTimePage'den gelen görsel widget listesini strateji önizleme alanına yansıtır.
        """
        if hasattr(self, "strategy_table_layout"):
            while self.strategy_table_layout.count():
                item = self.strategy_table_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # 🔧 Eksik olan başlık kısmını burada oluştur
            for i, w in enumerate(widgets):
                wrapper = QWidget()
                wrapper_layout = QVBoxLayout(wrapper)
                wrapper.setFixedWidth(300)
                wrapper_layout.setContentsMargins(0, 0, 0, 0)
                wrapper_layout.setSpacing(6)

                stint_label = QLabel(f"Stint {i + 1}")
                stint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                stint_label.setFixedWidth(300)  # 🔥 Hücre ile aynı genişlikte yap
                stint_label.setStyleSheet("""
                    color: white;
                    background-color: rgba(0, 0, 0, 0.5);
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 6px;
                """)

                wrapper_layout.addWidget(stint_label)
                w.setFixedWidth(300)
                wrapper_layout.addWidget(w)

                self.strategy_table_layout.addWidget(wrapper)

    def set_table_component(self, table_component):
        self.table_component = table_component

    def load_strategy_column(self, strategy_name: str):
        if not hasattr(self, "table_component"):
            print("TableComponent bağlantısı yok.")
            return

        # 🔄 Strateji kolon indexleri (fcy eklendi)
        index_map = {
            "strategy_a": 2,
            "strategy_b": 3,
            "strategy_c": 4,
            "strategy_d": 5,
            "strategy_fcy_auto": 6  # ✅ FCY sonrası öneri kolonu
        }

        col_index = index_map.get(strategy_name)
        if col_index is None:
            print("Geçersiz strateji adı:", strategy_name)
            return

        widgets = []
        for i in range(self.table_component.table.rowCount()):
            original = self.table_component.table.cellWidget(i, col_index)
            if original is None:
                continue

            clone = QWidget()
            clone.setFixedWidth(300)
            layout = QVBoxLayout(clone)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)

            # ✅ Sadece içerikler klonlanıyor, başlık yok
            fuel_row = QHBoxLayout()
            for child in original.findChildren(QLabel):
                label = QLabel(child.text())
                label.setStyleSheet(child.styleSheet())
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if "Fuel" in child.text() or "Virtual" in child.text():
                    fuel_row.addWidget(label)
                else:
                    layout.addWidget(label)

            layout.addLayout(fuel_row)
            widgets.append(clone)

        self.show_strategy_preview_widgets(widgets)
        self.highlight_active_stint()



    def on_strategy_changed(self):
        strategy_keys = ["strategy_a", "strategy_b", "strategy_c", "strategy_d"]
        index = self.strategy_combo.currentIndex()
        if 0 <= index < len(strategy_keys):
            self.selected_strategy = strategy_keys[index]
            self.load_strategy_column(self.selected_strategy)

    def update_finish_timer(self):
        if self.finish_time_left <= 0:
            self.finish_countdown.setText("Race Over!")
            self.finish_timer.stop()
            return

        # 🔴 Her saniyede aktif stint vurgusunu güncelle
        self.highlight_active_stint()

        self.finish_time_left -= 1
        hours = self.finish_time_left // 3600
        minutes = (self.finish_time_left % 3600) // 60
        seconds = self.finish_time_left % 60
        self.finish_countdown.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def highlight_active_stint(self):
        if not hasattr(self, "table_component"):
            return

        # ✅ FCY ile eklenen özel strateji adı da desteklenmeli
        strategy_keys = ["strategy_a", "strategy_b", "strategy_c", "strategy_d", "strategy_fcy_auto"]
        if self.selected_strategy not in strategy_keys:
            print("❌ Tanımsız strateji adı:", self.selected_strategy)
            return

        col_index = strategy_keys.index(self.selected_strategy) + 2

        for row in range(self.table_component.table.rowCount()):
            cell = self.table_component.table.cellWidget(row, col_index)
            if not cell:
                continue

            for child in cell.findChildren(QLabel):
                if "🟢 ACTIVE" in child.text():
                    new_text = child.text().replace("🟢 ACTIVE", "").strip()
                    child.setText(new_text)
                    child.setStyleSheet(child.styleSheet().replace("color: lime;", ""))

        found_active = False
        for row in range(self.table_component.table.rowCount()):
            if found_active:
                break

            cell = self.table_component.table.cellWidget(row, col_index)
            if not cell:
                continue

            for label in cell.findChildren(QLabel):
                if hasattr(label, "property") and label.property("highlighted"):
                    continue

                if "Remaining:" in label.text():
                    match = re.search(r"Remaining:\s*(\d+):(\d+):(\d+)", label.text())
                    if match:
                        h, m, s = map(int, match.groups())
                        remaining_secs = h * 3600 + m * 60 + s
                        if remaining_secs <= self.finish_time_left:
                            stint_label = cell.findChildren(QLabel)[0]
                            if "🟢 ACTIVE" not in stint_label.text():
                                stint_label.setProperty("highlighted", True)
                                stint_label.setText(f"{stint_label.text().split('🟢')[0].strip()}  🟢 ACTIVE")
                                stint_label.setStyleSheet("color: lime; font-weight: bold;")
                            found_active = True
                            break



    def toggle_finish_timer(self):
        if self.finish_timer_running:
            self.finish_timer.stop()
            self.finish_timer_running = False
            self.finish_start_pause_button.setText("▶")
        else:
            self.finish_timer.start(1000)
            self.finish_timer_running = True
            self.finish_start_pause_button.setText("⏸")

    def set_finish_time_seconds(self, seconds: int):
        self.finish_time_left = seconds
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        self.finish_countdown.setText(f"{h:02}:{m:02}:{s:02}")

        # ✅ Eğer daha önce hiç strateji seçilmemişse varsayılan olarak A'yı kullan
        if not hasattr(self, "selected_strategy"):
            self.selected_strategy = "strategy_a"

        self.highlight_active_stint()


    # 🎯 Strateji seçildiğinde çalışacak fonksiyon
    def refresh_strategy_preview(self):
        main_window = self.window()
        if hasattr(main_window, "page_drivers_time"):
            page = main_window.page_drivers_time
            strategy_name = page.selected_strategy
            widgets = page.get_cloned_strategy_widgets(strategy_name)

            # 👇 Driver adlarını sırayla al
            driver_names = []
            for i in range(len(widgets)):
                combo = page.table.cellWidget(i, 3)
                if isinstance(combo, QComboBox):
                    driver_names.append(combo.currentText().strip())
                else:
                    driver_names.append("")

            self.load_selected_strategy(widgets, driver_names)

    def start_timer(self, name):
        now = QDateTime.currentDateTime()

        if name == "pitlane" and self.pitlane_pause_time:
            # Devam et
            pause_duration = self.pitlane_pause_time.secsTo(now)
            self.pitlane_timer_start = self.pitlane_timer_start.addSecs(pause_duration)
            self.pitlane_pause_time = None
        else:
            setattr(self, f"{name}_timer_start", now)

        # FCY snapshot işlemi
        if name == "fcy":
            self.fcy_snapshot_label.setText(
                f"🕒 FCY Start:  {self.finish_countdown.text()}\n🕒 FCY Finish:  --:--:--"
            )
            self.trigger_adaptive_strategy()
            self.recalculate_fcy_strategy()  # FCY tablosunu doğrudan üret

        getattr(self, f"{name}_timer").start(1000)

    def stop_timer(self, name):
        getattr(self, f"{name}_timer").stop()

        now = QDateTime.currentDateTime()
        start_time = getattr(self, f"{name}_timer_start", None)

        if start_time:
            seconds = start_time.secsTo(now)

            # Pitlane özel durumu: duraklat
            if name == "pitlane" and getattr(self, "pitlane_pause_time", None) is None:
                self.pitlane_pause_time = now
                return  # gösterim güncellenmesin

            minutes = seconds // 60
            sec = seconds % 60
            time_str = f"{minutes:02}:{sec:02}"
            getattr(self, f"{name}_time_label").setText(f"⏱ {name.upper()}: {time_str}")

            # FCY finish snapshot
            if name == "fcy":
                current = self.fcy_snapshot_label.text()
                updated = re.sub(
                    r"🕒 FCY Finish:.*",
                    f"🕒 FCY Finish:  {QTime.currentTime().toString('HH:mm:ss')}",
                    current
                )
                self.fcy_snapshot_label.setText(updated)

    def update_fcy_timer(self):
        self._update_timer_label("fcy")

    def update_pitlane_timer(self):
        self._update_timer_label("pitlane")

    def update_pitzone_timer(self):
        self._update_timer_label("pitzone")

    def _update_timer_label(self, name):
        start_time = getattr(self, f"{name}_timer_start", None)
        if start_time:
            now = QDateTime.currentDateTime()
            seconds = start_time.secsTo(now)
            minutes = seconds // 60
            sec = seconds % 60
            time_str = f"{minutes:02}:{sec:02}"
            getattr(self, f"{name}_time_label").setText(f"⏱ {name.upper()}: {time_str}")

    def trigger_adaptive_strategy(self):
        # Kalan süreyi al ve sadece öneri panelini göster
        time_str = self.finish_countdown.text()
        try:
            h, m, s = map(int, time_str.split(":"))
            remaining = h * 3600 + m * 60 + s
            self.adaptive_strategy_widget.setVisible(True)
            self.recalculate_fcy_strategy()  # direkt tabloyu üret
        except Exception as e:
            print(f"❌ Süre okunamadı: {e}")


        except Exception as e:
            error_label = QLabel(f"❌ Süre alınamadı: {str(e)}")
            error_label.setStyleSheet("color: red; font-family: Poppins;")
            self.adaptive_strategy_layout.addWidget(error_label)
            self.adaptive_strategy_widget.setVisible(True)

    def on_adaptive_strategy_selected(self, strategy_text: str):
        print(f"📥 Seçilen strateji: {strategy_text}")

        try:
            import re
            match = re.search(r"(\d+)\s*x\s*(\d+)\s*dk", strategy_text)
            if not match:
                print("❌ Strateji formatı parse edilemedi:", strategy_text)
                return

            stint_count = int(match.group(1))
            stint_minutes = int(match.group(2))

            # 🔁 Mevcut finish countdown değerinden kalan saniyeyi hesapla
            finish_time = self.finish_countdown.text()
            h, m, s = map(int, finish_time.split(":"))
            remaining_secs = h * 3600 + m * 60 + s

            if hasattr(self, "table_component"):
                self.table_component.generate_fcy_strategy_column(
                    stint_count, stint_minutes, remaining_secs
                )

                self.selected_strategy = "strategy_fcy_auto"
                self.load_strategy_column("strategy_fcy_auto")
                self.adaptive_strategy_widget.setVisible(False)

        except Exception as e:
            print("❌ Strateji uygulama hatası:", e)

    def recalculate_fcy_strategy(self):
        try:
            # 🔄 Seçilen FCY taban stratejisi (A/B/C/D)
            base_index = self.fcy_base_strategy_combo.currentIndex()
            selected_key = ["strategy_a", "strategy_b", "strategy_c", "strategy_d"][base_index]

            if hasattr(self, "strategy_form"):
                stint_laps = int(self.strategy_form.strategy_inputs[selected_key].text())

                lap_time = parse_average_lap_time(self.strategy_form.lap_time())
                pit_time = int(self.strategy_form.pit_time())
                fuel_per_lap = float(str(self.strategy_form.fuel_per_lap()).replace(",", "."))
                virtual_per_lap = float(str(self.strategy_form.virtual_fuel_per_lap()).replace(",", "."))
                tire_consumption = float(str(self.strategy_form.tire_consumption()).replace(",", "."))

                h, m, s = map(int, self.finish_countdown.text().split(":"))
                remaining_secs = h * 3600 + m * 60 + s

                print("🔧 FCY strateji hesaplama:")
                print(f"   Seçilen strateji: {selected_key}")
                print(f"   Laps: {stint_laps}")
                print(f"   Lap time: {lap_time} saniye")
                print(f"   Pit time: {pit_time} saniye")
                print(f"   Fuel/lap: {fuel_per_lap} L")
                print(f"   Virtual fuel: {virtual_per_lap} L")
                print(f"   Tire consumption: {tire_consumption} %")
                print(f"   Kalan süre: {remaining_secs} saniye")

                self.draw_fcy_preview_table_from_laps(
                    stint_laps, lap_time, pit_time, remaining_secs, fuel_per_lap
                )

        except Exception as e:
            print("❌ FCY strateji hesaplama hatası:", e)

    def draw_fcy_preview_table_from_laps(self, stint_laps, lap_time_secs, pit_time_secs, total_time_secs, fuel_per_lap):
        print("📐 FCY Tablo çizimi başladı")
        print(f"➤️  stint_laps: {stint_laps}, lap_time_secs: {lap_time_secs}, pit_time_secs: {pit_time_secs}, total_time_secs: {total_time_secs}, fuel_per_lap: {fuel_per_lap}")

        if not hasattr(self, "strategy_form"):
            print("❌ strategy_form bağlı değil.")
            return

        try:
            fuel_time = int(self.strategy_form.fuel_time())
            tire_time = int(self.strategy_form.tire_time())
            virtual_per_lap = float(str(self.strategy_form.virtual_fuel_per_lap()).replace(",", "."))
            tire_per_stint = float(str(self.strategy_form.tire_consumption()).replace(",", "."))
        except Exception as e:
            print(f"❌ FCY tablo parametre okuma hatası: {e}")
            return

        while self.fcy_preview_layout.count():
            item = self.fcy_preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stint_list = []
        used_time = 0

        # Aktif stint indexini bul
        active_stint_index = -1
        if hasattr(self, "table_component"):
            for row in range(self.table_component.table.rowCount()):
                cell = self.table_component.table.cellWidget(row, 2)  # Strategy A
                if not cell:
                    continue
                for label in cell.findChildren(QLabel):
                    if "🌟 ACTIVE" in label.text():
                        active_stint_index = row
                        break
                if active_stint_index >= 0:
                    break

        while used_time + pit_time_secs + lap_time_secs <= total_time_secs:
            laps_this_stint = min(stint_laps, (total_time_secs - used_time - pit_time_secs) // lap_time_secs)
            if laps_this_stint <= 0:
                break

            stint_secs = laps_this_stint * lap_time_secs
            total_secs = stint_secs + pit_time_secs
            cumulative_total_secs = used_time + total_secs
            fuel_total = laps_this_stint * fuel_per_lap
            virtual_total = laps_this_stint * virtual_per_lap
            tire_total = laps_this_stint * tire_per_stint
            remaining_secs = max(0, total_time_secs - used_time - total_secs)

            print(f"🌯 Stint eklendi: laps={laps_this_stint}, time={total_secs}s, fuel={fuel_total:.2f}L, virtual={virtual_total:.2f}, tire={tire_total:.2f}%, remaining={remaining_secs}s")

            stint_list.append({
                "laps": laps_this_stint,
                "stint_secs": stint_secs,
                "total_secs": cumulative_total_secs,
                "fuel": fuel_total,
                "virtual": virtual_total,
                "tire": tire_total,
                "remaining": remaining_secs
            })

            used_time += total_secs

        for i, stint in enumerate(stint_list):
            cell = QWidget()
            cell.setStyleSheet("""
                background-color: #FFD700;
                border-radius: 6px;
                padding: 4px;
            """)
            layout = QVBoxLayout(cell)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(4)

            total_h = stint['total_secs'] // 3600
            total_m = (stint['total_secs'] % 3600) // 60
            total_s = stint['total_secs'] % 60

            labels = [
                QLabel(f"🔧 Stint Time: {stint['stint_secs'] // 60:02}:{stint['stint_secs'] % 60:02}"),
                QLabel(f"🔧 Pit Time: {pit_time_secs // 60:02}:{pit_time_secs % 60:02}"),
                QLabel(f"⏱️ Total Time: {total_h:02}:{total_m:02}:{total_s:02}"),
                QLabel(f"⏳ Remaining: {stint['remaining'] // 3600:02}:{(stint['remaining'] % 3600) // 60:02}:{stint['remaining'] % 60:02}"),
                QLabel(f"⛽ Fuel: {stint['fuel']:.2f} L"),
                QLabel(f"🔸 Virtual: {stint['virtual']:.2f}")
            ]

            for lbl in labels:
                lbl.setStyleSheet("""
                    color: black;
                    font-size: 13px;
                    font-family: Poppins;
                    font-weight: bold;
                """)
                layout.addWidget(lbl)

            self.fcy_preview_layout.addWidget(cell)

    def set_strategy_form(self, strategy_form):
        self.strategy_form = strategy_form

    def show_strategy_table(self):
        print("▶️ show_strategy_table() çağrıldı")

        if not hasattr(self, "strategy_form"):
            print("❌ strategy_form bağlı değil.")
            return

        strategy_data = self.strategy_form.get_strategy_data()

        # 👇 json_key dışarıdan set edilmiş olmalı
        if hasattr(self, "json_key"):
            strategy_data["json_key"] = self.json_key
        else:
            strategy_data["json_key"] = "default"

        print("📦 get_strategy_data sonucu:", strategy_data)

        #table_widget = generate_strategy_table(strategy_data)  # ✅ utils fonksiyonu

        # Önce temizle
        while self.strategy_table_layout.count():
            item = self.strategy_table_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        #self.strategy_table_layout.addWidget(table_widget)

    def toggle_fcy_timer(self):
        if self.fcy_timer.isActive():
            self.stop_timer("fcy")
            self.fcy_start_button.setText("▶ FCY")
        else:
            self.start_timer("fcy")
            self.fcy_start_button.setText("⏸ FCY")
































