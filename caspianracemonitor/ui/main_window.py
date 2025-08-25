from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QComboBox, QStackedWidget, QPushButton, QListWidgetItem, QHeaderView,
    QSystemTrayIcon, QMenu, QApplication, QScrollArea
)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QIcon, QAction
from PyQt6.QtCore import Qt, QSize, QLocale
QLocale.setDefault(QLocale(QLocale.Language.English))
from PyQt6.QtGui import QFontDatabase
import json
import os

from pages.home_page import HomePage
from pages.prerace_stint_calculator import PreRaceStintCalculator
from pages.drivers_time import DriversTimePage
from pages.live_race_monitor import LiveRaceMonitor
from pages.practice_data_analysis import PracticeDataAnalysis
from pages.teams_strategy_comparison import TeamsStrategyComparison
from pages.settings import SettingsDialog

from utils.resource_path import resource_path

class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.background = QPixmap(resource_path("assets/background.jpg"))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CaspianRaceMonitor")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = CentralWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        with open(resource_path("ui/styles.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        font_id = QFontDatabase.addApplicationFont(resource_path("assets/fonts/Race Sport.ttf"))
        if font_id == -1:
            print("Font yüklenemedi!")

        font_families = QFontDatabase.applicationFontFamilies(font_id)
        print("Font loaded families:", font_families)

        if font_families:
            race_sport_font = QFont(font_families[0], 36)
        else:
            race_sport_font = QFont("Arial", 36)

        top_area = QWidget()
        top_area.setStyleSheet("background-color: rgba(30, 30, 30, 0.8); border-radius: 10px;")
        top_area.setFixedHeight(160)
        top_layout = QHBoxLayout(top_area)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(15)

        self.toggle_button = QPushButton("\u2630")
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        header = QLabel()
        header.setPixmap(QPixmap(resource_path("assets/header/header.png")))
        header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setScaledContents(True)
        header.setFixedHeight(80)

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        header_container.setStyleSheet("background-color: transparent;")

        monitor_icon = QLabel()
        monitor_icon.setPixmap(QPixmap(resource_path("assets/icons/monitor.png")).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        header_layout.addWidget(monitor_icon)
        header_layout.addWidget(header)

        self.car_image_label = QLabel()
        self.car_image_label.setFixedSize(346, 100)
        self.car_image_label.setStyleSheet("background-color: transparent;")
        self.car_image_label.setScaledContents(True)

        self.class_selector = QComboBox()
        self.class_selector.setMaximumWidth(200)
        self.class_selector.setObjectName("TrackSelector")
        with open(resource_path('assets/cars.json'), 'r', encoding='utf-8') as f:
            self.cars_data = json.load(f)
        self.update_class_selector()
        self.class_selector.currentTextChanged.connect(self.update_car_selector)

        self.car_selector = QComboBox()
        self.car_selector.setMaximumWidth(200)
        self.car_selector.setObjectName("TrackSelector")
        self.update_car_selector(self.class_selector.currentText())
        self.car_selector.currentTextChanged.connect(self.update_car_image)

        self.track_selector = QComboBox()
        self.track_selector.setMaximumWidth(250)
        self.track_selector.setObjectName("TrackSelector")
        with open(resource_path('assets/tracks.json'), 'r', encoding='utf-8') as f:
            tracks_data = json.load(f)
        tracks = tracks_data["tracks"]
        for track in tracks:
            name = track["name"]
            icon_path = resource_path(f"assets/flags/{track['flag']}")
            flag_icon = QIcon(icon_path)
            self.track_selector.addItem(flag_icon, name)

        self.class_selector.currentTextChanged.connect(self.trigger_strategy_reload)
        self.car_selector.currentTextChanged.connect(self.trigger_strategy_reload)
        self.track_selector.currentTextChanged.connect(self.trigger_strategy_reload)

        self.profile_button = QPushButton()
        self.profile_button.setIcon(QIcon(resource_path("assets/icons/profile.png")))
        self.profile_button.setFixedSize(40, 40)

        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(resource_path("assets/icons/settings.png")))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings_dialog)

        top_layout.addWidget(self.toggle_button)
        top_layout.addWidget(header_container)
        top_layout.addWidget(self.car_image_label)

        selectors_layout = QVBoxLayout()
        selectors_layout.setSpacing(5)
        selectors_layout.addWidget(self.class_selector)
        selectors_layout.addWidget(self.car_selector)
        selectors_layout.addWidget(self.track_selector)
        top_layout.addLayout(selectors_layout)

        top_layout.addWidget(self.profile_button)
        top_layout.addWidget(self.settings_button)

        body_area = QWidget()
        body_layout = QHBoxLayout(body_area)
        body_layout.setContentsMargins(10, 10, 10, 10)
        body_layout.setSpacing(10)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        icons = {
            "Home": "assets/icons/home.png",
            "PreRace Stint Calculator": "assets/icons/prerace.png",
            "Drivers Time": "assets/icons/helmet.png",
            "Live Race Monitor": "assets/icons/live.png",
            "Practice Data Analysis": "assets/icons/stint.png",
            "Teams Strategy Comparison": "assets/icons/comparison.png"
        }
        for text, icon_path in icons.items():
            item = QListWidgetItem(text)
            item.setIcon(QIcon(resource_path(icon_path)))
            self.sidebar.addItem(item)

        self.sidebar.itemClicked.connect(self.change_page)

        self.content_area = QStackedWidget()
        self.page_home = HomePage()
        self.page_prerace = PreRaceStintCalculator()

        category = self.class_selector.currentText()
        brand = self.car_selector.currentText()
        track = self.track_selector.currentText()

        # ✅ LiveRaceMonitor önce oluşturulmalı
        scroll_area_live_monitor = QScrollArea()
        scroll_area_live_monitor.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        scroll_area_live_monitor.setWidgetResizable(True)

        self.page_live_monitor = LiveRaceMonitor()
        scroll_area_live_monitor.setWidget(self.page_live_monitor)
        self.page_live_monitor.set_table_component(self.page_prerace.table_component)
        self.page_live_monitor.set_strategy_form(self.page_prerace.strategy_form)

        # ✅ class/car/track bilgilerine göre json_key oluştur
        json_key = f"{category}_{brand}_{track}".lower()
        self.page_live_monitor.json_key = json_key

        # ✅ DriversTimePage sonra oluşturulur
        self.page_drivers_time = DriversTimePage()
        self.page_drivers_time.set_table_component(self.page_prerace.table_component)
        self.page_drivers_time.strategy_selected_callback = self.page_live_monitor.show_strategy_preview_widgets

        # ✅ Context güncellemesi
        self.page_prerace.strategy_form.set_current_context(category, brand, track)
        self.page_prerace.strategy_form.data_ready.connect(self.set_race_finish_timer_from_form)

        # ✅ RST'yi JSON'dan al ve sayaç için hedef zamanı ayarla
        from PyQt6.QtCore import QDateTime
        filename = os.path.join("data", "strategy_inputs", "hypercar_alpinea424_silverstonecircuit.json")
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                rst_string = data.get("start_time", "")
                rst_dt = QDateTime.fromString(rst_string, "dd MMM yyyy HH:mm")
                if rst_dt.isValid():
                    print("📦 JSON'dan RST:", rst_dt.toString("dd MMM yyyy HH:mm:ss"))
                    self.page_live_monitor.set_target_time(rst_dt)
                else:
                    print("❌ RST geçersiz:", rst_string)

        self.page_practice_analysis = PracticeDataAnalysis()
        self.page_teams_strategy = TeamsStrategyComparison()


        self.content_area.addWidget(self.page_home)
        self.content_area.addWidget(self.page_prerace)
        self.content_area.addWidget(self.page_drivers_time)
        self.content_area.addWidget(self.page_live_monitor)
        self.content_area.addWidget(self.page_practice_analysis)
        self.content_area.addWidget(self.page_teams_strategy)

        self.content_area.setCurrentIndex(0)

        body_layout.addWidget(self.sidebar)
        body_layout.addWidget(self.content_area, 1)

        main_layout.addWidget(top_area)
        main_layout.addWidget(body_area)

        self.update_car_image(self.car_selector.currentText())
        
        close_button = QPushButton("✕", self)
        close_button.setObjectName("HeaderButton")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.5);
                border-radius: 4px;
            }
        """)
        close_button.move(self.width() - 40, 10)
        close_button.clicked.connect(self.close)
        close_button.raise_()  # En öne al

        # Pencere boyutlanınca buton konumunu korusun
        def reposition_close_button():
            close_button.move(self.width() - 40, 10)

        self.resizeEvent = lambda event: reposition_close_button()
        self.init_tray_icon()


    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def change_page(self, item):
        text = item.text().strip()
        if text == "Home":
            self.content_area.setCurrentIndex(0)
        elif text == "PreRace Stint Calculator":
            self.content_area.setCurrentIndex(1)
        elif text == "Drivers Time":
            self.content_area.setCurrentIndex(2)
        elif text == "Live Race Monitor":
            self.content_area.setCurrentIndex(3)
        elif text == "Practice Data Analysis":
            self.content_area.setCurrentIndex(4)
        elif text == "Teams Strategy Comparison":
            self.content_area.setCurrentIndex(5)

    def update_car_selector(self, selected_class):
        self.car_selector.clear()
        cars = self.cars_data.get(selected_class, [])
        for car in cars:
            car_name = car["name"]
            brand_name = car["brand"]
            icon_path = resource_path(f"assets/brands/{brand_name}.png")
            icon = QIcon(icon_path)
            self.car_selector.addItem(icon, car_name)

    def update_class_selector(self):
        self.class_selector.clear()
        for class_name in self.cars_data.keys():
            icon_filename = class_name.lower().replace(" ", "") + ".png"
            icon_path = resource_path(os.path.join("assets/class", icon_filename))
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                self.class_selector.addItem(icon, class_name)
            else:
                self.class_selector.addItem(class_name)

    def update_car_image(self, selected_car):
        selected_class = self.class_selector.currentText()
        cars = self.cars_data.get(selected_class, [])
        for car in cars:
            if car["name"] == selected_car:
                car_img_path = resource_path(f"assets/cars/{selected_class.lower()}/{car['brand']}.png")
                if os.path.exists(car_img_path):
                    self.car_image_label.setPixmap(QPixmap(car_img_path))
                else:
                    self.car_image_label.clear()
                break

    def trigger_strategy_reload(self):
        category = self.class_selector.currentText()
        brand = self.car_selector.currentText()
        track = self.track_selector.currentText()
        self.page_prerace.strategy_form.set_current_context(category, brand, track)


    def resize_columns(self):
        try:
            self.page_prerace.table_component.table.resizeColumnsToContents()
            self.page_prerace.table_component.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception as e:
            print("resize_columns hatası:", e)
            
    def open_settings_dialog(self):
        dialog = SettingsDialog()
        if dialog.exec():
            team_name = dialog.team_input.text().strip()
            if team_name:
                self.page_drivers_time.set_current_team(team_name)

    def set_race_finish_timer_from_form(self, data: dict):
        race_time_seconds = data.get("race_time_seconds", 0)
        self.page_live_monitor.set_finish_time_seconds(race_time_seconds)

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(resource_path("assets/icons/crm_icon.ico")), self)
        self.tray_icon.setToolTip("Caspian Race Monitor")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: black;
                border: 1px solid #aaa;
                padding: 6px;
                font-size: 14px;
                font-family: Poppins;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
                color: black;
            }
        """)

        # ✅ Fullscreen action
        restore_action = QAction("Go Fullscreen", self)
        restore_action.triggered.connect(self.showFullScreen)
        tray_menu.addAction(restore_action)

        # ❌ Quit action
        quit_action = QAction("Exit Application", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()  # Single-click restores window

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()





