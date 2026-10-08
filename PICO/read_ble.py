"""
Python Desktop Client to read BLE BMP280 Temperature from Raspberry Pi Pico W (aioble)
Requires: pip install bleak
"""

import asyncio
from bleak import BleakScanner, BleakClient

# UUIDs matching main.py (Environmental Sensing Service & Temperature Characteristic)
SERVICE_UUID = "0000181a-0000-1000-8000-00805f9b34fb"
TEMP_CHAR_UUID = "00002a6e-0000-1000-8000-00805f9b34fb"

def handle_temp_notification(sender, data):
    # sint16 in 0.01 deg C
    raw_val = int.from_bytes(data, byteorder="little", signed=True)
    temp_celsius = raw_val / 100.0
    print(f"-> Live Notification [Temperature]: {temp_celsius:.2f} °C")

async def main():
    print("Searching for 'RPi-Pico' BLE device...")
    device = await BleakScanner.find_device_by_name("RPi-Pico", timeout=10.0)

    if not device:
        print("Device 'RPi-Pico' not found. Make sure Pico W is powered on and advertising.")
        return

    print(f"Found device: {device.name} [{device.address}]")
    async with BleakClient(device) as client:
        print(f"Connected to Pico W: {client.is_connected}")

        # Read initial temperature value
        temp_data = await client.read_gatt_char(TEMP_CHAR_UUID)
        raw_temp = int.from_bytes(temp_data, byteorder="little", signed=True)
        print(f"Initial Temperature Reading: {raw_temp / 100.0:.2f} °C")

        # Subscribe to notifications
        print("\nSubscribing to live temperature notifications (Press Ctrl+C to stop)...")
        await client.start_notify(TEMP_CHAR_UUID, handle_temp_notification)

        while True:
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnected.")
