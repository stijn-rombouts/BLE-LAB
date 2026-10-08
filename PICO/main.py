import asyncio
import aioble
import bluetooth
import struct
from micropython import const
from machine import Pin, I2C
from bmp280 import BMP280

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml (Generic Thermometer = 768)
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
# How frequently to send advertising beacons (250,000 microseconds = 250ms)
_ADV_INTERVAL_US = 250_000

# Pin Configuration for I2C (I2C0: GP4=SDA, GP5=SCL)
I2C_ID = 0
SDA_PIN = 4
SCL_PIN = 5
I2C_FREQ = 400_000

# Register GATT server (Environmental Sensing Service with Temperature characteristic)
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
)
aioble.register_services(temp_service)

def _encode_temperature(temp_c):
    """Encode temperature into sint16 in hundredths of a degree Celsius (0.01°C resolution)."""
    val = int(round(temp_c * 100))
    val = max(-32768, min(32767, val))
    return struct.pack("<h", val)

# Set initial non-empty value (20.00 °C) so GATT read never returns empty / N/A
temp_characteristic.write(_encode_temperature(20.0))

def init_led():
    """Attempt to initialize the onboard LED for visual feedback."""
    try:
        return Pin("LED", Pin.OUT)
    except Exception:
        try:
            return Pin(25, Pin.OUT)
        except Exception:
            return None

def init_bmp280():
    """Initialize I2C bus and BMP280 sensor."""
    print(f"Initializing I2C{I2C_ID} (SDA: GP{SDA_PIN}, SCL: GP{SCL_PIN})...")
    i2c = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)
    devices = i2c.scan()
    print(f"I2C Devices found: {[hex(d) for d in devices]}")

    if not devices:
        raise RuntimeError("No I2C devices detected! Please check your wiring.")

    bmp_addr = None
    for addr in (0x76, 0x77):
        if addr in devices:
            bmp_addr = addr
            break

    if bmp_addr is None:
        raise RuntimeError("BMP280 sensor not found at address 0x76 or 0x77!")

    print(f"BMP280 detected at address 0x{bmp_addr:02X}")
    return BMP280(i2c, address=bmp_addr)

async def sensor_task(sensor, led):
    """Periodically read temperature from BMP280 and update BLE characteristic."""
    while True:
        try:
            temp = sensor.temperature
            print(f"[BMP280 Telemetry] Temperature: {temp:.2f} °C")

            # Write updated value to GATT characteristic & send notification to connected clients
            temp_characteristic.write(_encode_temperature(temp), send_update=True)

            if led:
                led.on()
                await asyncio.sleep_ms(100)
                led.off()

        except Exception as e:
            print("Error reading BMP280 sensor:", e)

        await asyncio.sleep(2)

async def peripheral_task():
    """Manage BLE advertising and incoming central connections using aioble."""
    while True:
        print("Advertising BLE peripheral ('RPi-Pico')...")
        async with await aioble.advertise(
            _ADV_INTERVAL_US,
            name="RPi-Pico",
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print(f"BLE Central connected from {connection.device}")
            await connection.disconnected()
            print("BLE Central disconnected")

async def main():
    print("=" * 50)
    print(" Raspberry Pi Pico W - Async BLE BMP280 Thermometer")
    print(" Powered by aioble & asyncio")
    print("=" * 50)

    led = init_led()
    if led:
        led.off()

    sensor = init_bmp280()

    # Launch sensor reading task and BLE peripheral advertising task concurrently
    t1 = asyncio.create_task(sensor_task(sensor, led))
    t2 = asyncio.create_task(peripheral_task())

    await asyncio.gather(t1, t2)

if __name__ == "__main__":
    asyncio.run(main())
