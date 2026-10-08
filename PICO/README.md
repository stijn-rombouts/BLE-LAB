# Raspberry Pi Pico W - Async BLE BMP280 Thermometer Node

A MicroPython project using **`aioble`** and **`asyncio`** to read temperature measurements from a **BMP280 sensor** via I2C and transmit them over **Bluetooth Low Energy (BLE)** using the standard GATT Environmental Sensing Service.

---

## 🚀 Features

- **Modern Async BLE (`aioble`):** Powered by MicroPython's official `aioble` and `asyncio` libraries.
- **Single-Characteristic Focus:** Exposes **only the BMP280 temperature** reading over BLE (Environmental Sensing Service `0x181A`, Temperature Characteristic `0x2A6E`).
- **Precision BMP280 Driver:** High-accuracy MicroPython driver with Bosch compensation formulas.
- **Non-Blocking Operation:** `asyncio` task loop allows sensor sampling and BLE advertising/connection management to run concurrently.
- **Cross-Platform Compatibility:** Connect via mobile apps (nRF Connect, LightBlue) or desktop Python scripts (`bleak`).

---

## 📂 Project Architecture & File Structure

| File | Description |
| :--- | :--- |
| [`main.py`](file:///home/stijn/Documents/git/BLE-LAB/main.py) | Main application script utilizing `aioble` and `asyncio` for sensor sampling & BLE peripheral tasks. |
| [`bmp280.py`](file:///home/stijn/Documents/git/BLE-LAB/bmp280.py) | MicroPython driver for Bosch BMP280 I2C temperature/pressure sensor. |
| [`read_ble.py`](file:///home/stijn/Documents/git/BLE-LAB/read_ble.py) | Desktop Python script (using `bleak`) to scan and receive temperature notifications. |
| [`FLASHING_GUIDE.md`](file:///home/stijn/Documents/git/BLE-LAB/FLASHING_GUIDE.md) | Step-by-step instructions to flash MicroPython & install `aioble`. |
| [`WIRING.md`](file:///home/stijn/Documents/git/BLE-LAB/WIRING.md) | Wiring table and schematic diagram for Pico W to BMP280. |

---

## 🛠️ Quick Start

### 1. Hardware Setup
Connect the BMP280 to your Pico W as documented in [`WIRING.md`](file:///home/stijn/Documents/git/BLE-LAB/WIRING.md):
- **VCC** ➔ 3V3 (Pin 36)
- **GND** ➔ GND (Pin 38)
- **SDA** ➔ GP4 (Pin 6)
- **SCL** ➔ GP5 (Pin 7)

### 2. Install MicroPython & `aioble`
Follow [`FLASHING_GUIDE.md`](file:///home/stijn/Documents/git/BLE-LAB/FLASHING_GUIDE.md) to flash MicroPython and install `aioble`:
```bash
pip install mpremote
mpremote mip install aioble
```

### 3. Upload & Run
Copy `bmp280.py` and `main.py` onto your Pico W and execute:
```bash
mpremote cp bmp280.py main.py :
mpremote run main.py
```

---

## 📡 BLE GATT Specifications

| Element | UUID | Format | Resolution / Units | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Service** | `0x181A` | - | - | Environmental Sensing Service |
| **Characteristic: Temperature** | `0x2A6E` | `sint16` (Little Endian) | 0.01 °C | e.g., `2345` = 23.45 °C |

---

## 📲 Reading Data from Central Devices

### Option A: Mobile App (nRF Connect / LightBlue)
1. Open **nRF Connect** on iOS/Android and scan for BLE devices.
2. Locate **`PicoW-BMP280`** and tap **Connect**.
3. Open **Environmental Sensing Service** (`0x181A`).
4. Read or enable notifications on **Temperature** (`0x2A6E`).

### Option B: Desktop Python Client (`read_ble.py`)
Run the Python test client on your PC/Mac:
```bash
pip install bleak
python read_ble.py
```
Output:
```text
Searching for 'PicoW-BMP280' BLE device...
Found device: PicoW-BMP280 [XX:XX:XX:XX:XX:XX]
Connected to Pico W: True
Initial Temperature Reading: 22.84 °C

Subscribing to live temperature notifications...
-> Live Notification [Temperature]: 22.85 °C
```
