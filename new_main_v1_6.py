import machine
import sys
import uselect
import time

# --- Setup ---
led = machine.Pin('LED', machine.Pin.OUT)
try: led.off()
except: led = machine.Pin(25, machine.Pin.OUT)

fan_pwm = machine.PWM(machine.Pin(16))
fan_pwm.freq(25000)
fan_pwm.duty_u16(0)

# Serial Polling
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

# State
last_tick = time.ticks_ms()
timeout_ms = 15000
buffer = ""

# Hardware Watchdog
wdt = None
try: wdt = machine.WDT(timeout=8000)
except: pass

print("Pico Tesla P4 v1.6 ONLINE")

while True:
    if wdt: wdt.feed()
    
    # Heartbeat LED (Slow blink)
    led.value((time.ticks_ms() // 1000) % 2)
    
    # Robust Serial Reading (One char per loop)
    if spoll.poll(0):
        char = sys.stdin.read(1)
        if char in '\n\r':
            if buffer:
                try:
                    p = int(buffer)
                    p = max(0, min(100, p))
                    fan_pwm.duty_u16(int((p/100)*65535))
                    last_tick = time.ticks_ms()
                    print("ACK: {}%".format(p))
                except:
                    print("ERR")
                buffer = ""
        elif char in "0123456789":
            buffer += char
        elif char == '\x03': # Ctrl+C safety
            machine.reset()
            
    # Software Watchdog
    if time.ticks_diff(time.ticks_ms(), last_tick) > timeout_ms:
        if fan_pwm.duty_u16() > 0:
            fan_pwm.duty_u16(0)
            print("TIMEOUT: Fan Safety Off")
        last_tick = time.ticks_ms() # Reset timer to avoid spam
