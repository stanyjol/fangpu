#!/usr/bin/env python3

import time
import sys
import serial
from pynvml import *

# --- KONFIGURACE ---
SERIAL_PORT = '/dev/ttyACM0'  # Na Windows např. 'COM3'
BAUD_RATE = 115200
UPDATE_INTERVAL = 2           # v sekundách
GPU_INDEX = 0                 # Pokud máš v PC víc grafik, Tesla P4 bývá 0

# Teplotní křivka (Teplota: Procenta PWM)
TEMP_MIN = 40  # Pod 40°C větrák stojí (nebo jede na minimum)
TEMP_MAX = 65  # Nad 65°C větrák jede na 100%
PWM_MIN = 20   # Minimální rozběhové otáčky (aby motor nepískal a točil se)
PWM_MAX = 100

def get_fan_speed(temp):
    """Vypočítá procenta PWM na základě teploty."""
    if temp < TEMP_MIN:
        return 0
    if temp >= TEMP_MAX:
        return PWM_MAX
    
    # Lineární interpolace mezi MIN a MAX
    speed = PWM_MIN + (temp - TEMP_MIN) * (PWM_MAX - PWM_MIN) / (TEMP_MAX - TEMP_MIN)
    return int(speed)

def main():
    # Inicializace NVML (Nvidia driver API)
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(GPU_INDEX)
        device_name = nvmlDeviceGetName(handle)
        print(f"--- Monitoring zahájen: {device_name} ---")
    except NVMLError as err:
        print(f"Chyba inicializace NVML: {err}")
        return

    # Inicializace Sériové linky (Pico)
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Čekání na reboot Pica po otevření portu
    except serial.SerialException as err:
        print(f"Chyba portu {SERIAL_PORT}: {err}")
        return

    try:
        while True:
            # 1. Čtení teploty přímo z driveru
            temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            
            # 2. Výpočet rychlosti
            speed = get_fan_speed(temp)
            
            # 3. Odeslání do Pica (formát: "číslo\n")
            msg = f"{speed}\n"
            ser.write(msg.encode('utf-8'))
            
            print(f"GPU: {temp}°C | Fan: {speed}% | Status: OK", end='\r')
            
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\nUkončování... Nastavuji bezpečné otáčky.")
        ser.write(b"30\n") # Necháme dochladit na 30%
    except Exception as e:
        print(f"\nNeočekávaná chyba: {e}")
    finally:
        ser.close()
        nvmlShutdown()

if __name__ == "__main__":
    main()
