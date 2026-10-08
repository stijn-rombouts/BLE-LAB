# Flashing MicroPython & Installing `aioble` on Raspberry Pi Pico W

This document outlines the complete plan and step-by-step instructions for flashing MicroPython firmware onto your Raspberry Pi Pico W board, installing the **`aioble`** library, and setting up the development environment.

---

## Step 1: Download MicroPython UF2 Firmware

1. Open your web browser and navigate to the official MicroPython download page:
   - **For Raspberry Pi Pico W (RP2040):** [MicroPython Pico W Firmware](https://micropython.org/download/RPI_PICO_W/)
   - **For Raspberry Pi Pico 2 W (RP2350):** [MicroPython Pico 2 W Firmware](https://micropython.org/download/RPI_PICO2_W/)
2. Download the latest **stable** `.uf2` release file (v1.20 or newer recommended for `asyncio`/`mip` support).

---

## Step 2: Put Raspberry Pi Pico W into BOOTSEL Mode

1. Unplug the USB cable from your Raspberry Pi Pico W.
2. Press and hold the white **BOOTSEL** button on the board.
3. Plug the USB cable into your computer while continuing to hold the button.
4. Release the BOOTSEL button.
5. Your computer will mount a new USB mass storage device named **`RPI-RP2`**.

---

## Step 3: Flash MicroPython Firmware

1. Drag the downloaded `.uf2` file and drop it into the **`RPI-RP2`** drive volume.
2. The drive will automatically unmount and the Pico W will reboot into MicroPython.



---

## Step 4: Install `aioble` Library

The project relies on MicroPython's official **`aioble`** package for asynchronous Bluetooth LE communication.

Run the following command on your host computer:
```bash
pip install mpremote
mpremote mip install aioble
```
This automatically fetches `aioble` from the MicroPython Package Index (`micropython-lib`) and copies it into `/lib/aioble` on your Pico W.

---

## Step 5: Upload Project Code to Pico W

Upload `bmp280.py` and `main.py` to the root filesystem of the Pico W:

From the `BLE-LAB` directory on your computer:
```bash
mpremote cp bmp280.py main.py :
```

---

## Step 6: Test Execution

To execute `main.py` directly from your host terminal:
```bash
mpremote run main.py
```
*(When saved as `main.py` on the device root, it automatically runs whenever the board powers up).*
