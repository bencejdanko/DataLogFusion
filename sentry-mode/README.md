# Poor Man's Sentry Mode (QNX 8.0 & Laptop Broadcast)

This system reads a physical IR obstacle sensor on a Raspberry Pi (running QNX 8.0), captures camera frames natively on trigger using the QNX Sensor Framework, and streams them to a laptop server which broadcasts them via Cloudflare Tunnel (`sentry.visiondustry.com`).

---

## 1. Laptop Setup

### A. Start the Broadcast Server
Run the broadcast receiver on your laptop (port `8080`):
```bash
python sentry-mode/laptop_sentry_server.py
```
*Make sure your Cloudflare Tunnel (`sentry.visiondustry.com`) is running and pointing to `http://localhost:8080`.*

### B. Compile the Capture Utility (Already done!)
If you ever need to recompile the native camera utility from your Windows laptop, open a Command Prompt and run:
```cmd
# Load the QNX toolchain environment variables
C:\Users\bence\qnx800\qnxsdp-env.bat

# Cross-compile for the Pi target
cd sentry-mode
qcc -Vgcc_ntoaarch64le -o camera_capture camera_capture.c -lcamapi
```

---

## 2. Raspberry Pi Setup (QNX 8.0)

### A. Copy Drivers and Configuration to the Pi
From the `sentry-mode` directory on your host laptop, copy the files one by one:

```bash
scp -o MACs=hmac-sha2-256 rpi5_camera_module3_custom.conf "C:\Users\bence\qnx800\target\qnx\aarch64le\usr\lib\libimx708_external_camera.so" "C:\Users\bence\qnx800\target\qnx\aarch64le\usr\lib\libsensor_platform_broadcom_rpi5.so" camera_capture pi_sentry_client.py qnxuser@172.20.10.7:/data/home/qnxuser/
```

```bash
# Stop the running sensor daemon
sudo slay sensor

# Create a writable roll directory for sensor files
mkdir -p /data/home/qnxuser/roll

# Start the sensor daemon with the physical camera config in the background
sudo sensor -U 521:521,1001 -b external -r /data/home/qnxuser/roll -c /data/home/qnxuser/rpi5_camera_module3_custom.conf &
```

### B. Run the Sentry Client
SSH into your Raspberry Pi and start the Python controller:
```bash
# SSH onto the Pi
ssh qnxuser@172.20.10.7
# ssh -m hmac-sha2-256 qnxuser@172.20.10.7

# Run the controller (monitors IR sensor)
python pi_sentry_client.py

# OR force continuous streaming for testing (bypasses IR sensor)
python pi_sentry_client.py --test
```

### C. Downsampling & Network Timeout Configuration
By default, the client is configured to downsample the frame to improve stream reliability and frame rate over local network connections (e.g., mobile hotspots).
You can configure these settings inside [pi_sentry_client.py](file:///c:/Users/bence/Downloads/x-cube-mems1/Projects/NUCLEO-F401RE/Applications/IKS5A1/DataLogFusion/sentry-mode/pi_sentry_client.py):
* `DOWNSAMPLE_FACTOR`: Set to `2` by default (resolution drops to `640x360`, saving 75% bandwidth). Set to `1` for full raw `1280x720`.
* `POST_TIMEOUT`: Set to `5.0` seconds by default (prevents connection drops on slow uploads).

---

## 3. How to Test
1. Wave your hand in front of the IR Obstacle Sensor.
2. The Pi's physical feedback LED on **GPIO 20** will turn ON.
3. The Pi client script will run the native `camera_capture` binary in the background.
4. The binary will capture a raw frame, output its dimensions, and the Python client will POST the raw buffer over the local network to your laptop.
5. Your laptop will convert NV12/BGRx pixels into JPEG and serve the live feed. Have your teammates open `https://sentry.visiondustry.com/stream.mjpg` to view it!
