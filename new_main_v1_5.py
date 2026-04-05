import machine
import sys
import uselect
import time

# --- Konfigurace ---
# Onboard LED (Pico/Pico W)
led = machine.Pin('LED', machine.Pin.OUT)
try:
    led.off()
except:
    led = machine.Pin(25, machine.Pin.OUT)

# HW PWM na GP16
fan_pin = machine.Pin(16)
fan_pwm = machine.PWM(fan_pin)
fan_pwm.freq(25000)
fan_pwm.duty_u16(0)

def main_loop():
    poll_object = uselect.poll()
    poll_object.register(sys.stdin, uselect.POLLIN)
    
    last_tick = time.ticks_ms()
    timeout_ms = 15000 # Soft-watchdog (vypnutí fanu)
    last_led = time.ticks_ms()
    
    # Hardware Watchdog (restart Pica při záseku)
    try:
        wdt = machine.WDT(timeout=8000)
    except:
        wdt = None
        print("WDT not available")
        
    print("Pico chlazeni Tesla P4 v1.5 ONLINE (WDT enabled)")
    buffer = ""
    
    while True:
        if wdt: wdt.feed()
        now = time.ticks_ms()
        
        # 1. Heartbeat LED (bliká každých 250ms)
        if time.ticks_diff(now, last_led) > 250:
            led.value(not led.value())
            last_led = now
            
        # 2. Zpracování sériové linky
        events = poll_object.poll(0) # Nečekat
        for obj, mask in events:
            if mask & uselect.POLLIN:
                # Načíst vše co je v bufferu
                while True:
                    char = sys.stdin.read(1)
                    if char in ('\n', '\r'):
                        if buffer:
                            try:
                                p = int(buffer)
                                p = max(0, min(100, p))
                                fan_pwm.duty_u16(int((p/100)*65535))
                                last_tick = time.ticks_ms()
                                print("ACK: {}%".format(p))
                            except:
                                print("ERR: '{}'".format(buffer))
                            buffer = ""
                        break # Další event
                    elif char in "0123456789":
                        buffer += char
                    
                    # Kontrola zda je v bufferu další znak k přečtení
                    if not poll_object.poll(0):
                        break
            elif mask & (uselect.POLLHUP | uselect.POLLERR):
                buffer = "" # Reset při chybě spojení

        # 3. Software Watchdog (Vypnutí fanu při neaktivitě PC)
        if time.ticks_diff(now, last_tick) > timeout_ms:
            if fan_pwm.duty_u16() > 0:
                fan_pwm.duty_u16(0)
                print("WATCHDOG: Timeout (Fan OFF)")
            last_tick = now # Nezahlcovat linku

# Spuštění s odchycením chyb
try:
    main_loop()
except Exception as e:
    print("FATAL ERROR:", e)
    time.sleep(2)
    machine.reset()
