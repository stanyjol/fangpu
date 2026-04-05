# Tesla P4 Active Cooling System

An active cooling solution for the passive **NVIDIA Tesla P4** graphics card using an external blower fan controlled by a **Raspberry Pi Pico**.

## 📋 Overview
The system reads the GPU temperature from the host PC and dynamically adjusts the fan speed using a PWM signal.

## 🛠 Hardware Configuration
- **Controller:** Raspberry Pi Pico (RP2040)
- **Power Transistor:** IRLZ34N (Logic Level N-MOSFET) for 3.3V PWM control
- **Method:** Low-side switching (switching the negative terminal of the fan)
- **PWM Pin:** GP16 (Physical Pin 21)

| Component | Connection |
| :--- | :--- |
| **RPi Pico GP16** | Gate (via 220R resistor) |
| **IRLZ34N Gate** | GP16 & 10k pull-down to GND |
| **IRLZ34N Drain** | Fan (-) |
| **IRLZ34N Source** | GND |

## 🚀 Software
- **Pico (MicroPython):** `new_main_v1_6.py` (includes Hardware Watchdog and 25kHz PWM)
- **Host (Linux):** `tesla_fan_control.py` (Python script to read GPU temperature via NVML)

## ⚙️ Usage
To manually test or control the fan:
```bash
python3 test_fan.py
```
*(Communicates at 115200 baud for stable performance)*

---
*Created for efficient cooling of passive server-grade GPUs.*
