#!/usr/bin/env python3
"""
Raspberry Pi 3B+ BLE Central Client & Matplotlib Telemetry Visualizer
Reads BMP280 temperature over BLE from Raspberry Pi Pico W ('RPi-Pico')
and plots real-time temperature graph using Matplotlib.
"""

import asyncio
import os
import struct
import time
from collections import deque

import matplotlib
# Use non-interactive backend if no DISPLAY server is detected
if not os.environ.get('DISPLAY'):
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

from bleak import BleakScanner, BleakClient

# GATT UUIDs matching Pico W main.py
SERVICE_UUID = "0000181a-0000-1000-8000-00805f9b34fb"
TEMP_CHAR_UUID = "00002a6e-0000-1000-8000-00805f9b34fb"
TARGET_NAME = "RPi-Pico"

# Save plot file in same directory as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_FILE = os.path.join(SCRIPT_DIR, "temperature_plot.png")

# Data buffers for plotting (stores last 60 samples)
MAX_SAMPLES = 60
timestamps = deque(maxlen=MAX_SAMPLES)
temperatures = deque(maxlen=MAX_SAMPLES)
sample_count = 0

def update_plot():
    """Update Matplotlib temperature plot and save to temperature_plot.png."""
    if not temperatures:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    plt.style.use('ggplot')
    
    ax.plot(list(timestamps), list(temperatures), color='#e74c3c', linewidth=2.5, marker='o', label='BMP280 Temperature (°C)')
    
    # Clean single-line title
    ax.set_title('Raspberry Pi Pico W - BLE Temperature Telemetry', 
                 fontsize=13, fontweight='bold', color='#2c3e50', pad=15)
    
    ax.set_xlabel('Time (seconds since start)', fontsize=11)
    ax.set_ylabel('Temperature (°C)', fontsize=11)
    
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper left')
    fig.tight_layout()
    
    # 1. Save plot image to script directory
    fig.savefig(PLOT_FILE, dpi=120)

    # 2. Also save to current working directory if different
    cwd_plot = os.path.abspath("temperature_plot.png")
    if os.path.abspath(PLOT_FILE) != cwd_plot:
        try:
            fig.savefig(cwd_plot, dpi=120)
        except Exception:
            pass

    # 3. If /root is writable and different, also save there for safety
    root_plot = "/root/temperature_plot.png"
    if os.path.isdir("/root") and os.access("/root", os.W_OK) and os.path.abspath(PLOT_FILE) != root_plot:
        try:
            fig.savefig(root_plot, dpi=120)
        except Exception:
            pass

    plt.close(fig)
    print(f"[Visualization] Updated plot saved (Latest: {temperatures[-1]:.2f} °C, Total samples: {len(temperatures)})")

async def find_pico_device():
    """Discover Pico W by name or known MAC address with retry loop."""
    print(f"Scanning for BLE device ('{TARGET_NAME}')...")
    attempt = 0
    while True:
        attempt += 1
        devices = await BleakScanner.discover(timeout=4.0)
        for d in devices:
            if (d.name and TARGET_NAME.lower() in d.name.lower()) or d.address.upper() == "28:CD:C1:0E:A4:EC":
                return d
        print(f"  [Attempt #{attempt}] '{TARGET_NAME}' not found yet. Retrying in 2s (make sure phone/other central is disconnected)...")
        await asyncio.sleep(2.0)

async def main():
    global sample_count
    start_time = time.time()

    print("=" * 60)
    print(" Raspberry Pi 3B+ BLE Central Client (Matplotlib Visualizer)")
    print(" Target Device Name:", TARGET_NAME)
    print(" Target Characteristic UUID:", TEMP_CHAR_UUID)
    print(" Plot File Target:", PLOT_FILE)
    print("=" * 60)

    device = await find_pico_device()

    print(f"\n[SUCCESS] Found device '{device.name}' at [{device.address}]")
    print(f"Connecting to {device.address}...")

    async with BleakClient(device) as client:
        print(f"Connected to Pico W: {client.is_connected}")

        # Polling loop matching the assignment slide (image2.png)
        print("\nStarting periodic temperature read loop (every 2s)...")
        while client.is_connected:
            try:
                data = await client.read_gatt_char(TEMP_CHAR_UUID)
                raw_val = struct.unpack("<h", data)[0]
                temp_c = raw_val / 100.0
                elapsed = round(time.time() - start_time, 1)
                sample_count += 1

                print(f"[Sample #{sample_count} at {elapsed}s] Raw: {raw_val} -> Temperature: {temp_c:.2f} °C")

                timestamps.append(elapsed)
                temperatures.append(temp_c)

                update_plot()
            except Exception as e:
                print(f"Error reading characteristic: {e}")

            await asyncio.sleep(2.0)

        print("Pico W disconnected.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnected by user.")
