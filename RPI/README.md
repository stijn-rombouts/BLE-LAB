# Raspberry Pi 3B+ BLE Central Client & Telemetry Visualization

This folder contains the plan, code, and documentation for **Part 2** of the assignment: connecting a **Raspberry Pi 3B+** over Bluetooth LE to the **Raspberry Pi Pico W** sensor node.

---

## 📂 Folder Structure

| Path | Description |
| :--- | :--- |
| [`PLAN.md`](file:///home/stijn/Documents/git/BLE-LAB/RPI/PLAN.md) | Detailed plan, step-by-step setup guide, and code architecture for BLE client & visualization. |
| [`Assignment/`](file:///home/stijn/Documents/git/BLE-LAB/RPI/Assignment) | Course assignment slides (`image.png`, `image2.png`, `image3.png`). |

---

## 📌 Summary of Steps

1. **System Prep:** Create Python `venv` and install `bleak`, `matplotlib`, `paho-mqtt`.
2. **BLE Central Client:** Scan for `RPi-Pico`, connect, and subscribe to Temperature characteristic (`0x2A6E`).
3. **Data Visualization:** Real-time plot using **Matplotlib** (local) or **MQTT to ThingSpeak** (cloud dashboard).

