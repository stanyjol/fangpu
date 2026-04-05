# Projekt: Inteligentní chlazení NVIDIA Tesla P4 (v1.0)

## 📋 Přehled projektu
Cílem je aktivní chlazení pasivní grafické karty NVIDIA Tesla P4 pomocí radiálního ventilátoru z laptopu (Sunon, 5V, 1.6W). Řízení probíhá na základě reálné teploty GPU vyčítané z hostitelského PC (Linux/Windows) přes sběrnici USB do mikrokontroleru Raspberry Pi Pico.

### Klíčové parametry:
- **Cílová teplota:** < 65 °C v plné zátěži.
- **HW platforma:** Raspberry Pi Pico (RP2040).
- **Výkonový prvek:** IRLZ34N (Logic Level N-MOSFET).
- **Komunikace:** USB Serial (přes MicroPython `sys.stdin`).

---

## 🛠 Hardwarové zapojení (Low-side Switching)

Zapojení využívá společnou zem (GND) a spínání záporného pólu ventilátoru.

| Součástka | Pin / Vývod | Připojení k | Poznámka |
| :--- | :--- | :--- | :--- |
| **RPi Pico** | VBUS (Pin 40) | Ventilátor (+) | Napájení 5V z USB |
| **RPi Pico** | GND (Pin 38) | Zdroj (-) & Source | Společná zem je kritická |
| **RPi Pico** | GP16 (Pin 21) | Gate (Pin 1) | PWM signál (3.3V) |
| **IRLZ34N** | Gate (Pin 1) | GP16 | Logic Level MOSFET |
| **Rezistor 220R** | Mezi GP16 a Gate | Gate | Ochrana pinu Pica |
| **Rezistor 10k** | Mezi Gate a GND | GND | Pull-down (vypnutí při resetu) |
| **IRLZ34N** | Drain (Pin 2) | Ventilátor (-) | Spínaný uzel |
| **IRLZ34N** | Source (Pin 3) | GND | Zem |
| **Dioda 1N4007** | Paralelně k fanu | (+) na VBUS, (-) na Drain | Ochrana proti indukci |

> **⚠️ Diagnostická poznámka:** BS170 se ukázal jako nevhodný pro 3.3V logiku Pica (vysoký vnitřní odpor při nízkém Vgs). IRLZ34N je nutné zapojit s ohledem na pinout G-D-S.

---
## 🐍 Software: Raspberry Pi Pico (MicroPython)

Ukládá se jako `main.py` do kořenového adresáře Pica.

```python
import machine
import sys
import uselect
import time

# Konfigurace PWM - PWM pin GP16 (fyzický pin 21)
fan_pin = machine.Pin(16)
fan_pwm = machine.PWM(fan_pin)
fan_pwm.freq(25000) # 25kHz je standard pro PC ventilátory, tiché a efektivní
fan_pwm.duty_u16(0)

# Příprava USB vstupu
poll_object = uselect.poll()
poll_object.register(sys.stdin, uselect.POLLIN)

last_tick = time.ticks_ms()
timeout_ms = 15000 # 15s Fail-safe (vypnutí při ztrátě dat z PC)

print("Pico chlazeni Tesla P4 v1.2 ONLINE (GP16, 25kHz)")

while True:
    # Kontrola vstupu ze sériové linky
    if poll_object.poll(100):
        line = sys.stdin.readline().strip()
        if line:
            try:
                # Očekáváme číslo 0-100
                percent = int(line)
                percent = max(0, min(100, percent))

                # Přepočet 0-100% na 0-65535 (16-bit PWM)
                duty = int((percent / 100) * 65535)
                fan_pwm.duty_u16(duty)

                # Reset watchdogu
                last_tick = time.ticks_ms()
                print("ACK: Fan set to {}%".format(percent))
            except ValueError:
                print("ERR: Invalid input '{}'".format(line))

    # Watchdog: Pokud PC přestane posílat data, vypni fan
    if time.ticks_diff(time.ticks_ms(), last_tick) > timeout_ms:
        if fan_pwm.duty_u16() > 0:
            fan_pwm.duty_u16(0)
            print("WATCHDOG: Fan disabled (timeout)")
```

