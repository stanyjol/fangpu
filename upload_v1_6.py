import serial
import time

PORT = '/dev/ttyACM0'
FILENAME = 'new_main_v1_6.py'

with open(FILENAME, 'r') as f:
    content = f.read()

try:
    with serial.Serial(PORT, 115200, timeout=2) as ser:
        print(f"Uploading {FILENAME}...")
        for _ in range(15):
            ser.write(b'\x03')
            time.sleep(0.05)
        ser.write(b'\r\n')
        time.sleep(0.5)
        ser.read_all()
        ser.write(b"f = open('main.py', 'w')\r\n")
        time.sleep(0.2)
        for line in content.split('\n'):
            escaped_line = line.replace('\\', '\\\\').replace("'", "\\'")
            cmd = f"f.write('{escaped_line}\\n')\r\n".encode()
            ser.write(cmd)
            time.sleep(0.05)
        ser.write(b"f.close()\r\n")
        time.sleep(0.5)
        ser.write(b"\x04")
        time.sleep(1)
        print("Upload complete. LED should blink every 1s.")
except Exception as e:
    print(f"Error: {e}")
