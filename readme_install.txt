# Installation Guide: Tesla P4 Active Cooling

This guide provides instructions for deploying the Tesla P4 fan control system on a Linux-based host.

## Prerequisites
- A target machine with a NVIDIA GPU and appropriate drivers installed.
- Python 3 and `python3-venv` installed.
- Raspberry Pi Pico connected via USB.

## Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/stanyjol/fangpu.git
   cd fangpu
   ```

2. **Prepare the environment:**
   Create a virtual environment and install the required dependencies:
   ```bash
   python3 -m venv fan_env
   source fan_env/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   deactivate
   ```

3. **Deploy as a Systemd Service:**
   To ensure the script runs automatically in the background:

   - Copy the service file to your systemd directory (adjust paths if necessary):
     ```bash
     sudo cp tesla-fan.service /etc/systemd/system/
     ```
   - Edit `/etc/systemd/system/tesla-fan.service` to ensure the `WorkingDirectory` and `ExecStart` paths point to your installation directory.
   - Enable and start the service:
     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable --now tesla-fan
     ```

## Troubleshooting
- **Serial Port:** Ensure your user has permissions to access the serial port (usually `/dev/ttyACM0`). You may need to add your user to the `dialout` group: `sudo usermod -a -G dialout $USER` (re-login required).
- **GPU Driver:** Ensure NVIDIA Management Library (NVML) is accessible by the user running the service.
- **Hardware:** Ensure the RPi Pico is flashed with `main.py` from this repository.
