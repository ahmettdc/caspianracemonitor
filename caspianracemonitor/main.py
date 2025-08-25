# main.py
import sys
import os

# ✅ YÜKSEK DPI SCALING DEVRE DIŞI BIRAKILIYOR
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt6.QtCore import QTimer

# .exe içinde çalışırken dosya yolu düzeltici
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # QSS stil dosyasını yükle
    try:
        qss_path = resource_path("ui/styles.qss")
        with open(qss_path, "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except Exception as e:
        print(f"Stil dosyası yüklenemedi: {e}")

    window = MainWindow()

    # 🔽 Bu ayar True olursa uygulama sadece tray'de başlar (pencere gizli)
    tray_only_start = False

    if tray_only_start:
        window.hide()
    else:
        window.showFullScreen()
        QTimer.singleShot(100, window.resize_columns)

    sys.exit(app.exec())
