# 📡 ESP32 Wi-Fi Radar (MicroPython)

[🇷🇺 Русская версия](#-русская-версия) | [🇬🇧 English Version](#-english-version)

---

## 🇷🇺 Русская версия

Автономный круговой Wi-Fi радар (сонар) на базе микроконтроллера **ESP32** и цветного дисплея **ST7789**. Прибор сканирует радиоэфир на частоте 2.4 ГГц, отображает найденные роутеры и точки доступа на экране в реальном времени, оценивает дистанцию до них по уровню сигнала (RSSI) и подаёт звуковые и световые импульсы при прохождении луча через цель.

### ✨ Основные возможности
* **Круговой сонар в реальном времени:** Плавное вращение луча без использования тяжёлых кадровых буферов памяти.
* **Дальномер сигнала:** Чем ближе источник сигнала, тем ближе метка к центру экрана и тем ярче её цвет (зелёный → жёлтый → красный).
* **Звук и световая индикация:** При обнаружении цели пьезопищалка издаёт сонарный импульс (в стиле счётчика Гейгера), а красный светодиод синхронно вспыхивает.
* **Нижняя панель телеметрии:** Отображает графическую шкалу мощности ближайшего роутера и точечный счётчик всех обнаруженных сетей вокруг.
* **Подключение без лишних GND:** Для пищалки и светодиода в коде реализованы виртуальные «минусы» на цифровых пинах.

### 🛠 Необходимые компоненты
1. Плата разработки **ESP32** с прошивкой MicroPython и встроенным C-драйвером `st7789`.
2. Цветной TFT-дисплей **ST7789 240×240** (интерфейс SPI).
3. Пассивная **пьезопищалка** (зуммер).
4. **Красный светодиод** (желательно с резистором 220–330 Ом).
5. Соединительные провода (DuPont).

### 🔌 Схема подключения проводов (Распиновка)

| Компонент | Контакт на модуле | Пин на ESP32 | Примечание |
| :--- | :--- | :--- | :--- |
| **Дисплей ST7789** | `GND` | `GND` | Общий минус |
| **Дисплей ST7789** | `VCC` | `3V3` | Питание 3.3 В |
| **Дисплей ST7789** | `SCK` (SCL) | `D18` | Тактовый сигнал SPI |
| **Дисплей ST7789** | `MOSI` (SDA) | `D23` | Передача данных SPI |
| **Дисплей ST7789** | `RES` (RST) | `D4` | Сброс дисплея |
| **Дисплей ST7789** | `DC` | `D2` | Выбор данные/команда |
| **Дисплей ST7789** | `BLK` | `D15` | Управление подсветкой |
| **Дисплей ST7789** | `CS` *(если есть)* | `GND` | Притянуть к минусу |
| **Пьезопищалка** | Ножка 1 (`+`) | `D25` | ШИМ-выход звука (PWM) |
| **Пьезопищалка** | Ножка 2 (`-`) | `D14` | Программный «минус» (`value=0`) |
| **Красный светодиод** | Длинная ножка (`+`) | `D33` | Индикатор обнаружения цели |
| **Красный светодиод** | Короткая ножка (`-`) | `D26` | Программный «минус» (`value=0`) |

> **Примечание:** Если на вашей плате отсутствует пин `D26`, подключите минус светодиода к пину `D27` или `D13` и измените номер пина в файле `main.py`.

### 🚀 Как запустить
1. Прошейте **ESP32** сборкой MicroPython с поддержкой C-драйвера `st7789` (например, *russhughes/st7789_mpy*).
2. Откройте среду **Thonny**, подключитесь к плате и загрузите файл `main.py` в корень памяти устройства.
3. Нажмите **F5** или перезагрузите плату кнопкой **EN** — радар запустится автоматически.

---

## 🇬🇧 English Version

An autonomous circular Wi-Fi radar (sonar) built on the **ESP32** microcontroller and a **ST7789** color TFT display. The device scans the 2.4 GHz radio spectrum, plots nearby routers and mobile hotspots on the screen in real time, estimates distance based on signal strength (RSSI), and triggers audio-visual alerts whenever the radar beam sweeps across a target.

### ✨ Key Features
* **Real-Time Circular Sonar:** Smooth rotating sweep beam rendered directly via C-driver primitives without heavy framebuffers.
* **Signal Distance Estimation:** Closer networks appear nearer to the center with color-coded intensity (Green → Yellow → Red).
* **Geiger-Style Audio & Visual Alerts:** A passive piezo buzzer emits a sonar blip and a red LED flashes synchronously when a target is detected.
* **Bottom Telemetry Bar:** Displays a live signal strength meter for the nearest router and a dot counter for all detected networks.
* **Virtual GND Pins:** Uses GPIO pins configured as `LOW` outputs to power the buzzer and LED without needing extra `GND` headers.

### 🛠 Hardware Requirements
1. **ESP32** development board flashed with MicroPython containing the C-based `st7789` driver.
2. **ST7789 240×240** IPS/TFT display (SPI interface).
3. Passive **piezo buzzer**.
4. **Red LED** (optional 220–330 Ω current-limiting resistor).
5. DuPont jumper wires.

### 🔌 Wiring & Pinout

| Component | Module Pin | ESP32 Pin | Notes |
| :--- | :--- | :--- | :--- |
| **ST7789 Display** | `GND` | `GND` | Common ground |
| **ST7789 Display** | `VCC` | `3V3` | 3.3V power |
| **ST7789 Display** | `SCK` (SCL) | `D18` | SPI clock |
| **ST7789 Display** | `MOSI` (SDA) | `D23` | SPI data |
| **ST7789 Display** | `RES` (RST) | `D4` | Display reset |
| **ST7789 Display** | `DC` | `D2` | Data/Command control |
| **ST7789 Display** | `BLK` | `D15` | Backlight control |
| **ST7789 Display** | `CS` *(if present)* | `GND` | Tie to ground |
| **Piezo Buzzer** | Pin 1 (`+`) | `D25` | PWM audio output |
| **Piezo Buzzer** | Pin 2 (`-`) | `D14` | Virtual GND (`value=0`) |
| **Red LED** | Long leg (`+`) | `D33` | Target detection indicator |
| **Red LED** | Short leg (`-`) | `D26` | Virtual GND (`value=0`) |

> **Note:** If your ESP32 board variant does not have a `D26` pin, connect the LED cathode to `D27` or `D13` and update the pin number in `main.py`.

### 🚀 Installation & Usage
1. Flash your **ESP32** with a MicroPython firmware build that includes the `st7789` C-driver (e.g., *russhughes/st7789_mpy*).
2. Open **Thonny IDE**, connect to your board, and upload `main.py` to the root directory of the MicroPython device.
3. Press **F5** or hit the **EN** reset button on the board to launch the radar automatically.
