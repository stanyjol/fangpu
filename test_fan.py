#!/usr/bin/python3

import serial
import time
import sys

# Konfigurace
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200 

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(1) 
        ser.reset_input_buffer()
        
        print(f"--- Tesla P4 Control (Baud: {BAUD_RATE}) ---")
        print("Enter 0-100 or Ctrl+C to exit.")

        while True:
            if ser.in_waiting:
                response = ser.read_all().decode('utf-8', errors='ignore')
                for line in response.split('\n'):
                    if line.strip():
                        print(f"Pico: {line.strip()}")

            try:
                user_input = input("\nPower [%]: ")
                if not user_input: continue
                val = int(user_input)
                if 0 <= val <= 100:
                    ser.write(f"{val}\n".encode('utf-8'))
                    ser.flush()
                else:
                    print("Error: 0-100 only.")
            except EOFError: break
            except ValueError: print("Error: Invalid number.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open: ser.close()

if __name__ == "__main__":
    main()
