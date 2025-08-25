# pages/strategy_utils.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

def calculate_total_time(stint_time_seconds, pit_time_seconds):
    """
    Total stint time = pure stint time + pit stop time
    """
    return stint_time_seconds + pit_time_seconds

def calculate_fuel_used(fuel_per_lap, laps):
    """
    Fuel consumption = fuel per lap * number of laps
    """
    return fuel_per_lap * laps

def estimate_total_laps(race_duration_minutes, average_lap_time_seconds):
    """
    Estimate total number of laps in a race
    """
    total_seconds = race_duration_minutes * 60
    if average_lap_time_seconds == 0:
        return 0
    return total_seconds / average_lap_time_seconds

def calculate_required_pit_stops(total_laps, stint_laps):
    """
    Calculate required pit stops based on stint laps
    """
    if stint_laps == 0:
        return 0
    return int(total_laps // stint_laps)

# ===========================
# Input Parsing Fonksiyonları
# ===========================

def parse_race_time(text: str) -> int:
    """
    hh:mm:ss formatındaki Race Time'ı toplam saniyeye çevirir.
    """
    if text:
        try:
            h, m, s = map(int, text.split(":"))
            return h * 3600 + m * 60 + s
        except Exception:
            print(f"Race Time formatı hatalı: {text}")
            return 0
    return 0

def parse_average_lap_time(text: str) -> float:
    """
    mm:ss.milisecond formatındaki Average Lap Time'ı toplam saniyeye çevirir.
    """
    if text:
        try:
            minute, second = text.split(":")
            minute = int(minute)
            second = float(second.replace(",", "."))
            return minute * 60 + second
        except Exception:
            print(f"Average Lap Time formatı hatalı: {text}")
            return 0.0
    return 0.0

def parse_integer(text: str) -> int:
    """
    Input'u integer (tamsayı) olarak parse eder.
    """
    try:
        return int(text)
    except Exception:
        print(f"Integer parse hatası: {text}")
        return 0

def parse_float_one_decimal(text: str) -> float:
    """
    Tek ondalıklı float olarak parse eder.
    """
    try:
        return round(float(text.replace(",", ".")), 1)
    except Exception:
        print(f"Float 1 decimal parse hatası: {text}")
        return 0.0

def parse_float_two_decimal(text: str) -> float:
    """
    İki ondalıklı float olarak parse eder.
    """
    try:
        return round(float(text.replace(",", ".")), 2)
    except Exception:
        print(f"Float 2 decimal parse hatası: {text}")
        return 0.00

# ===========================
# Yeni Ekstra Fonksiyonlar
# ===========================

def format_time(seconds: float) -> str:
    """
    Saniyeyi hh:mm:ss formatına çevirir.
    """
    if seconds < 0:
        seconds = 0
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{sec:02}"

def calculate_stint_time(avg_lap_time_seconds: float, stint_laps: int) -> float:
    """
    Bir stint süresini hesaplar.
    """
    return avg_lap_time_seconds * stint_laps

def calculate_time_left(race_time_seconds: float, elapsed_time_seconds: float) -> float:
    """
    Yarıştan kalan süreyi hesaplar.
    """
    return max(race_time_seconds - elapsed_time_seconds, 0)

# 🎯 FCY anında kalan süreye göre strateji önerileri
def generate_adaptive_strategies(remaining_secs: int) -> list[str]:
    """
    Kalan süreye göre önerilen strateji listesi üretir.
    Her öneri farklı stint dağılımları verir (örneğin 2x60dk, 3x40dk).
    """
    suggestions = []

    # Her stint ortalama süresi (örnek: 40dk, 45dk, 50dk)
    stint_durations = [50 * 60, 45 * 60, 40 * 60]  # saniye cinsinden

    for duration in stint_durations:
        stint_count = remaining_secs // duration
        leftover = remaining_secs % duration

        if stint_count >= 1:
            suggestions.append(
                f"{stint_count} x {duration // 60} dk + {leftover // 60} dk ek"
            )

    return suggestions

# def generate_strategy_table(strategy_data: dict) -> QWidget:
#     widget = QWidget()
#     layout = QVBoxLayout(widget)
#     layout.setContentsMargins(4, 4, 4, 4)
#     layout.setSpacing(6)

#     try:
#         laps_per_stint = int(strategy_data.get("strategy_a", 11))
#         total_seconds = parse_time_to_seconds(strategy_data.get("race_time", "24:00:00"))
#         lap_time = parse_lap_time(strategy_data.get("average_lap_time", "04:00.000"))
#         pit_time = int(strategy_data.get("pit_lane_time", 22))
#         fuel_per_lap = float(strategy_data.get("fuel_consumption", 7.5))
#         virtual_per_lap = float(strategy_data.get("virtual_fuel", 10.0))
#         tire_per_lap = float(strategy_data.get("tire_consumption", 2.5))
#     except Exception as e:
#         label = QLabel(f"Hesaplama hatası: {e}")
#         label.setStyleSheet("color: red")
#         layout.addWidget(label)
#         return widget

#     used_time = 0
#     stint_index = 1

#     while used_time + lap_time + pit_time <= total_seconds:
#         stint_laps = min(laps_per_stint, (total_seconds - used_time - pit_time) // lap_time)
#         if stint_laps <= 0:
#             break

#         stint_time = stint_laps * lap_time
#         total_stint = stint_time + pit_time

#         fuel_amount = stint_laps * fuel_per_lap
#         virtual_amount = stint_laps * virtual_per_lap
#         remaining = total_seconds - used_time - total_stint

#         print(f"🟩 Stint {stint_index}:")
#         print(f"   Stint Time: {format_seconds(stint_time)}")
#         print(f"   Pit Time:   {format_seconds(pit_time)}")
#         print(f"   Total Time: {format_seconds(total_stint)}")
#         print(f"   Remaining:  {format_seconds(remaining)}")
#         print(f"   Fuel:       {fuel_amount:.2f}L")
#         print(f"   Virtual:    {virtual_amount:.2f}")

#         box = QWidget()
#         box.setStyleSheet("""
#             background-color: rgba(30, 30, 30, 0.75);
#             border-radius: 10px;
#         """)
#         box.setMaximumWidth(380)
#         box_layout = QVBoxLayout(box)
#         box_layout.setContentsMargins(6, 6, 6, 6)
#         box_layout.setSpacing(4)

#         stint_label = QLabel(f"🟣 Stint Time: {format_seconds(stint_time)}")
#         stint_label.setStyleSheet("background-color: #001F3F; color: white; font-weight: bold; border-radius: 4px; padding: 4px;")

#         pit_label = QLabel(f"🎀 Pit Time: {format_seconds(pit_time)}")
#         pit_label.setStyleSheet("background-color: #FFD700; color: black; font-weight: bold; border-radius: 4px; padding: 4px;")

#         total_label = QLabel(f"⏱ Total Time: {format_seconds(total_stint)}")
#         total_label.setStyleSheet("background-color: #666; color: white; font-weight: bold; border-radius: 4px; padding: 4px;")

#         remaining_label = QLabel(f"⏳ Remaining: {format_seconds(remaining)}")
#         remaining_label.setStyleSheet("background-color: #cc4444; color: white; font-weight: bold; border-radius: 4px; padding: 4px;")

#         fuel_row = QWidget()
#         fuel_layout = QHBoxLayout()
#         fuel_layout.setContentsMargins(0, 0, 0, 0)
#         fuel_layout.setSpacing(6)

#         fuel_label = QLabel(f"🚀 Fuel: {fuel_amount:.2f}L")
#         fuel_label.setStyleSheet("background-color: green; color: white; border-radius: 4px; padding: 4px;")

#         virtual_label = QLabel(f"⚠️ Virtual: {virtual_amount:.2f}%")
#         virtual_label.setStyleSheet("background-color: purple; color: white; border-radius: 4px; padding: 4px;")

#         fuel_layout.addWidget(fuel_label)
#         fuel_layout.addWidget(virtual_label)
#         fuel_row.setLayout(fuel_layout)

#         box_layout.addWidget(stint_label)
#         box_layout.addWidget(pit_label)
#         box_layout.addWidget(total_label)
#         box_layout.addWidget(remaining_label)
#         box_layout.addWidget(fuel_row)

#         layout.addWidget(box)

#         used_time += total_stint
#         stint_index += 1

#     return widget

def parse_time_to_seconds(time_str: str) -> int:
    try:
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 86400

def parse_lap_time(text: str) -> int:
    try:
        m, rest = text.split(":")
        s = float(rest)
        return int(int(m) * 60 + s)
    except:
        return 240

def format_seconds(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{int(m):02}:{int(s):02}"
