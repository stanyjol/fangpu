import machine
import sys
import uselect

# Nastavení PWM na pinu GP15
fan_pwm = machine.PWM(machine.Pin(15))
fan_pwm.freq(25000) # Frekvence 25kHz (běžná pro ventilátory, nepíská)

# Výchozí stav - vypnuto
fan_pwm.duty_u16(0)

# Nastavení pro čtení ze sériové linky (USB)
poll_object = uselect.poll()
poll_object.register(sys.stdin, uselect.POLLIN)

last_update = machine.time_pulse_us(machine.Pin(15), 1) # Jen inicializace času
timeout_ms = 10000 # 10 sekund bez dat = vypnout

print("Pico chlazeni Tesla P4 bezi...")

while True:
    # Kontrola, zda přišla data z USB (PC skript)
    if poll_object.poll(100): # Čekej 100ms na data
        line = sys.stdin.readline().strip()
        try:
            # Očekáváme hodnotu 0 až 100 (procenta výkonu)
            percent = int(line)
            percent = max(0, min(100, percent))
            
            # Přepočet na 16-bit rozlišení MicroPythonu (0-65535)
            duty = int((percent / 100) * 65535)
            fan_pwm.duty_u16(duty)
            
            # Reset watchdogu (uložení aktuálního času v ms)
            last_tick = machine.ticks_ms()
        except ValueError:
            pass 

    # Watchdog: Pokud uplynulo moc času od posledních dat, vypni ventilátor
    if machine.ticks_diff(machine.ticks_ms(), last_tick) > timeout_ms:
        fan_pwm.duty_u16(0)

