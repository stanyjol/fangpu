#!/usr/bin/python3

import serial
import time
import sys

# Nastav port podle svého systému
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200 # Změněno na 115200 pro MicroPython default

def main():
    try:
        # Připojení k Picu
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(1) # Počkej na inicializaci po otevření portu
        
        # Vyčisti vstupní buffer
        ser.reset_input_buffer()
        
        print(f"--- Diagnostika chlazení Tesla P4 (Baud: {BAUD_RATE}) ---")
        print("Zadávej hodnotu 0 až 100 a potvrď Enterem. (Ctrl+C pro konec)")

        while True:
            # Čtení odpovědí z Pica (pokud nějaké jsou)
            if ser.in_waiting:
                response = ser.read_all().decode('utf-8', errors='ignore')
                for line in response.split('\n'):
                    if line.strip():
                        print(f"Pico: {line.strip()}")

            # Uživatelský vstup
            try:
                # Pomocí select by to bylo lepší, ale pro jednoduchost:
                user_input = input("\nZadej výkon [%]: ")
                if not user_input:
                    continue
                    
                val = int(user_input)
                if 0 <= val <= 100:
                    # Odeslání do Pica
                    msg = f"{val}\n"
                    ser.write(msg.encode('utf-8'))
                    ser.flush()
                else:
                    print("Chyba: Zadej číslo mezi 0 a 100.")
            except EOFError:
                break
            except ValueError:
                print("Chyba: Neplatný vstup.")

    except serial.SerialException as e:
        print(f"Chyba portu: {e}")
    except KeyboardInterrupt:
        print("\nUkončeno uživatelem.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
