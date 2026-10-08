import time
import struct

class BMP280:
    """
    MicroPython driver for the Bosch BMP280 Temperature and Barometric Pressure Sensor via I2C.
    """
    # BMP280 Registers
    REG_ID = 0xD0
    REG_RESET = 0xE0
    REG_STATUS = 0xF3
    REG_CTRL_MEAS = 0xF4
    REG_CONFIG = 0xF5
    REG_PRESS_MSB = 0xF7
    REG_CALIB_00 = 0x88

    # Default I2C Addresses
    ADDR_PRIMARY = 0x76
    ADDR_SECONDARY = 0x77

    def __init__(self, i2c, address=ADDR_PRIMARY):
        self.i2c = i2c
        self.address = address

        # Verify chip ID (BMP280 chip ID is 0x58, BME280 is 0x60)
        chip_id = self._read_reg(self.REG_ID, 1)[0]
        if chip_id not in (0x58, 0x60):
            raise RuntimeError(f"BMP280 not found at address 0x{address:02X} (Chip ID read: 0x{chip_id:02X})")

        self.reset()
        time.sleep_ms(100)

        self._read_calibration()
        self._configure()

    def _read_reg(self, reg, length):
        return self.i2c.readfrom_mem(self.address, reg, length)

    def _write_reg(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def reset(self):
        """Soft reset the sensor."""
        self._write_reg(self.REG_RESET, 0xB6)

    def _read_calibration(self):
        """Read 24 bytes of calibration data from 0x88 to 0x9F."""
        b = self._read_reg(self.REG_CALIB_00, 24)
        # Unpack Little-Endian:
        # dig_T1: unsigned short (H)
        # dig_T2, dig_T3: signed short (h)
        # dig_P1: unsigned short (H)
        # dig_P2..dig_P9: signed short (h)
        cal = struct.unpack("<HhhHhhhhhhhh", b)
        self.dig_T1 = cal[0]
        self.dig_T2 = cal[1]
        self.dig_T3 = cal[2]

        self.dig_P1 = cal[3]
        self.dig_P2 = cal[4]
        self.dig_P3 = cal[5]
        self.dig_P4 = cal[6]
        self.dig_P5 = cal[7]
        self.dig_P6 = cal[8]
        self.dig_P7 = cal[9]
        self.dig_P8 = cal[10]
        self.dig_P9 = cal[11]

    def _configure(self):
        """Set normal mode, 16x pressure oversampling, 2x temp oversampling, IIR filter coefficient 16."""
        # Config register: standby 0.5ms (000), IIR filter 16 (100), SPI 4-wire (0) -> 0b00010000 = 0x10
        self._write_reg(self.REG_CONFIG, 0x10)
        # Ctrl Meas: osrs_t x2 (010), osrs_p x16 (101), mode normal (11) -> 0b01010111 = 0x57
        self._write_reg(self.REG_CTRL_MEAS, 0x57)

    def read_raw(self):
        """Read raw uncompensated pressure and temperature values."""
        data = self._read_reg(self.REG_PRESS_MSB, 6)
        raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        raw_temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return raw_temp, raw_press

    def read_compensated_data(self):
        """
        Calculates compensated temperature (°C) and pressure (hPa).
        Returns a tuple (temperature_celsius, pressure_hpa).
        """
        raw_temp, raw_press = self.read_raw()

        # Temperature Compensation
        var1 = (raw_temp / 16384.0 - self.dig_T1 / 1024.0) * self.dig_T2
        var2 = ((raw_temp / 65536.0 - self.dig_T1 / 8192.0) ** 2) * self.dig_T3
        t_fine = var1 + var2
        temperature = t_fine / 5120.0

        # Pressure Compensation
        var1 = (t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = (var2 / 4.0) + (self.dig_P4 * 65536.0)
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1

        if var1 == 0:
            pressure = 0.0
        else:
            p = 1048576.0 - raw_press
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = self.dig_P9 * p * p / 2147483648.0
            var2 = p * self.dig_P8 / 32768.0
            pressure = (p + (var1 + var2 + self.dig_P7) / 16.0) / 100.0  # Convert Pa to hPa

        return temperature, pressure

    @property
    def temperature(self):
        """Return temperature in °C."""
        t, _ = self.read_compensated_data()
        return t

    @property
    def pressure(self):
        """Return pressure in hPa."""
        _, p = self.read_compensated_data()
        return p

