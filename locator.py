"""
ESP32 Wi-Fi Radar (MicroPython)
Круговой сонар для поиска Wi-Fi сетей 2.4 ГГц с визуализацией на дисплее ST7789,
звуковой индикацией (эффект счётчика Гейгера) и световой сигнализацией.

Подключение пинов:
- Дисплей ST7789: SCK -> D18, MOSI -> D23, RES -> D4, DC -> D2, BLK -> D15
- Пьезопищалка:   Ножка 1 -> D25, Ножка 2 -> D14 (виртуальный GND)
- Светодиод:      Плюс (+) -> D33, Минус (-) -> D26 (виртуальный GND)
"""

import gc
import network
import math
import time
from machine import Pin, SPI, PWM
import st7789

# 1. Инициализация Wi-Fi модуля в режиме сканера (STA_IF)
wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(0.3)
wlan.active(True)
time.sleep(0.3)

# Снижаем пиковую мощность передатчика для защиты от просадки напряжения (Brownout)
try:
    wlan.config(txpower=8)
except Exception:
    pass

gc.collect()

# 2. Инициализация быстрого C-драйвера дисплея ST7789 (240x240)
spi = SPI(2, baudrate=40000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(23))
tft = st7789.ST7789(
    spi, 240, 240,
    reset=Pin(4, Pin.OUT),
    dc=Pin(2, Pin.OUT),
    backlight=Pin(15, Pin.OUT),
    rotation=0
)
tft.init()
tft.fill(st7789.BLACK)

# 3. Настройка пьезопищалки и красного светодиода (без использования пинов GND)
Pin(14, Pin.OUT, value=0)  # Виртуальный GND для пищалки
buzzer = PWM(Pin(25))
buzzer.duty(0)

Pin(26, Pin.OUT, value=0)  # Виртуальный GND для светодиода
led_red = Pin(33, Pin.OUT, value=0)

# Цветовая палитра (RGB565)
BLACK      = st7789.BLACK
WHITE      = st7789.WHITE
GREEN      = st7789.color565(0, 255, 70)
DARK_GREEN = st7789.color565(0, 95, 25)
RED        = st7789.color565(255, 30, 30)
YELLOW     = st7789.color565(255, 220, 0)

# Геометрия радара
CX, CY = 120, 102
RADIUS = 92

# Глобальные переменные состояния эфира
targets = []
best_ssid = "SCANNING..."
best_rssi = -100


def blip_sound(strong=False):
    """Издаёт короткий сонарный импульс и мигает светодиодом при обнаружении цели."""
    led_red.value(1)
    buzzer.freq(1500 if strong else 950)
    buzzer.duty(150)  # Умеренная скважность для экономии тока
    time.sleep_ms(18 if strong else 8)
    buzzer.duty(0)
    led_red.value(0)


def draw_grid():
    """Отрисовывает координатную сетку и кольца дальности сонара."""
    tft.circle(CX, CY, RADIUS, DARK_GREEN)
    tft.circle(CX, CY, 62, DARK_GREEN)
    tft.circle(CX, CY, 31, DARK_GREEN)
    tft.hline(CX - RADIUS, CY, RADIUS * 2, DARK_GREEN)
    tft.vline(CX, CY - RADIUS, RADIUS * 2, DARK_GREEN)


def update_telemetry():
    """Обновляет нижнюю панель: шкалу мощности ближайшего роутера и счётчик сетей."""
    tft.fill_rect(0, 198, 240, 42, BLACK)
    tft.hline(0, 198, 240, DARK_GREEN)

    # Шкала уровня сигнала (RSSI) слева
    bars = max(1, min(10, (best_rssi + 100) // 6))
    for i in range(bars):
        col = RED if i > 7 else (YELLOW if i > 4 else GREEN)
        tft.fill_rect(10 + i * 11, 206, 8, 12, col)

    # Точечный индикатор количества найденных сетей справа (до 12 точек)
    for i in range(min(12, len(targets))):
        tft.fill_rect(140 + (i % 6) * 14, 206 + (i // 6) * 14, 8, 8, GREEN)


def scan_wifi():
    """Сканирует Wi-Fi сети вокруг и пересчитывает их координаты на радаре."""
    global targets, best_ssid, best_rssi

    # Выключаем периферию на время сканирования для стабильности питания
    buzzer.duty(0)
    led_red.value(0)

    try:
        nets = wlan.scan()
        new_targets = []
        top_rssi = -120
        top_name = "NO SIGNAL"

        for net in nets:
            ssid = net[0].decode("utf-8", "ignore").strip()
            if not ssid:
                ssid = "HIDDEN_NET"
            rssi = net[3]

            if rssi > top_rssi:
                top_rssi = rssi
                top_name = ssid

            # Переводим RSSI (-30..-95 dBm) в дистанцию от центра радара (14..88 пикс)
            clamped = max(-95, min(-30, rssi))
            dist = int(14 + ((-30 - clamped) / 65.0) * 74)

            # Вычисляем стабильный условный азимут (угол) по хешу имени сети
            angle = (sum(bytearray(ssid.encode())) * 137) % 360
            rad = math.radians(angle)
            new_targets.append((rad, dist, rssi, angle))

        # Стираем старые метки целей перед отрисовкой новых
        for rad, dist, rssi, t_angle in targets:
            tx = int(CX + dist * math.cos(rad))
            ty = int(CY + dist * math.sin(rad))
            tft.fill_rect(tx - 4, ty - 4, 9, 9, BLACK)

        targets = new_targets
        best_ssid = top_name
        best_rssi = top_rssi
        print("Найдено сетей:", len(targets), "| Ближайшая:", best_ssid, best_rssi, "dBm")
        update_telemetry()
    except Exception as e:
        print("Ошибка сканирования:", e)


# Стартовая инициализация экрана и первый скан эфира
draw_grid()
scan_wifi()

angle_deg = 0
prev_ex, prev_ey = CX, CY
last_scan = time.ticks_ms()

# Главный цикл анимации сонара
while True:
    now = time.ticks_ms()

    # Фоновое пересканирование эфира каждые 5.5 секунд
    if time.ticks_diff(now, last_scan) > 5500:
        scan_wifi()
        last_scan = now

    # Стираем предыдущий луч и восстанавливаем сетку
    tft.line(CX, CY, prev_ex, prev_ey, BLACK)
    draw_grid()

    # Рисуем новый луч радара
    rad_beam = math.radians(angle_deg)
    ex = int(CX + (RADIUS - 2) * math.cos(rad_beam))
    ey = int(CY + (RADIUS - 2) * math.sin(rad_beam))
    tft.line(CX, CY, ex, ey, GREEN)
    prev_ex, prev_ey = ex, ey

    # Отрисовка обнаруженных точек доступа и звуковой отклик при проходе луча
    for rad, dist, rssi, t_angle in targets:
        tx = int(CX + dist * math.cos(rad))
        ty = int(CY + dist * math.sin(rad))
        diff = (angle_deg - t_angle) % 360

        if diff < 8:
            tft.fill_rect(tx - 3, ty - 3, 7, 7, WHITE)
            if diff < 5:
                blip_sound(strong=(rssi > -55))
        else:
            col = RED if rssi > -55 else (YELLOW if rssi > -75 else GREEN)
            tft.fill_rect(tx - 2, ty - 2, 5, 5, col)

    angle_deg = (angle_deg + 5) % 360
    time.sleep_ms(18)
