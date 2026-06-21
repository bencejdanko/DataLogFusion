# QNX Streaming to Redis Database

Streams live MEMS sensor data from the STM32 board (connected via USB-serial at
`/dev/serusb1`) to the shared Redis Cloud stream **`/data/mems`** using a
single, dependency-free C program: **`main.c`**.

No external libraries are required — only standard POSIX sockets and termios,
which QNX Neutrino supports natively.

---

## File Overview

| File | Description |
|------|-------------|
| `main.c` | Self-contained C streamer (QNX / any POSIX target) |
| `redis_stream.py` | Python streamer (Windows / Linux / WSL2) |
| `README.md` | General setup notes |
| `README_QNX.md` | This file — QNX-specific build instructions |

---

## Redis Stream Details

| Property | Value |
|----------|-------|
| **Endpoint** | `hospitable-van-guitar-57111.db.redis.io:17434` |
| **Stream key** | `/data/mems` |
| **User** | `default` |
| **Fields per entry** | `ts, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, mag_x, mag_y, mag_z, press, roll, pitch, yaw` |
| **Protocol** | Raw RESP over TCP (no TLS) |

---

## Detecting the Serial Device on QNX

When the STM32 board is connected via USB, QNX exposes it through a
**USB-serial resource manager** (`devc-serusb`).  Use the steps below to
find the correct device path before running the streamer.

### 1. List available serial devices

```sh
ls /dev/ser*
```

QNX may enumerate the USB-serial adapter as either:
- **`/dev/serusb1`** — when `devc-serusb` creates a dedicated namespace
- **`/dev/ser10`** (or similar number) — when the system `devc-serusb` assigns the next available serial slot

Use whichever path appears. Confirm data is flowing:

```sh
cat /dev/ser10        # adjust number as needed
```

You should see CSV lines scrolling at ~100 Hz. Press `Ctrl+C` to stop.

### 3. If no device appears — start the USB-serial driver

QNX does not always auto-start `devc-serusb`.  Start it manually:

```sh
chmod +x devc-serusb
devc-serusb &
```

Then re-check `ls /dev/serusb*`.  On some QNX images the driver is
`devc-serusb2` or needs a specific USB path argument — check your BSP docs.

### 4. Pass the device to the streamer

```sh
# Use the detected device (default is already /dev/serusb1)
./mems_stream /dev/serusb1

# If enumerated as serusb2, serusb3, etc.
./mems_stream /dev/serusb2
```

---

## Building on QNX (native compile on the target)

If your QNX image includes a C compiler (`cc`):

```sh
# first on host machine copy over

scp -o MACs=hmac-sha2-256 main.c qnxuser@172.20.10.7:/data/home/qnxuser

# On the QNX Raspberry Pi target
cc -o mems_stream main.c -lsocket
```
# Default: /dev/serusb1 @ 115200 baud
./mems_stream

# Override serial device
./mems_stream /dev/serusb2
```

The program prints a startup banner and then logs a line every 10 samples
(~100 ms at 100 Hz):

```
==================================================
 STM32 MEMS → Redis Streamer  (QNX / C)
==================================================
Serial device : /dev/serusb1  @ 115200 baud
Redis endpoint: hospitable-van-guitar-57111.db.redis.io:17434
Redis stream  : /data/mems
Batch size    : 10 samples
--------------------------------------------------
Opening serial port...
Serial port opened.
Connecting to Redis...
TCP connection established.
Authenticated to Redis.
Streaming started. Press Ctrl+C to stop.

[10]  Pushed 10 samples to /data/mems
[20]  Pushed 10 samples to /data/mems
...
```

Press **Ctrl+C** to stop cleanly.

---

## Runtime Environment Variable Overrides

You can override the compiled-in Redis credentials at runtime without
recompiling:

```sh
export REDIS_HOST="hospitable-van-guitar-57111.db.redis.io"
export REDIS_PORT="17434"
export REDIS_PASS=
./mems_stream
```