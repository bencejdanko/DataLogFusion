# DataLogFusion Backend

Reads sensor data from the STM32 NUCLEO-F401RE over serial (115200 8N1) and streams it to Redis.

## Data Flow

```
STM32 NUCLEO (USB Serial)
        │  CSV lines @ 115200 8N1
        ▼
serial_reader.py  ──queue──▶  redis_publisher.py
                                    │
                        ┌───────────┴──────────────┐
                        ▼                          ▼
                 sensor:stream              sensor:latest
               (Redis Stream)              (Redis Hash)
               full time-series           latest snapshot
```

## Redis Keys

| Key | Type | Description |
|---|---|---|
| `sensor:stream` | Stream | Full time-series via `XADD` (capped at 50 000 entries) |
| `sensor:latest` | Hash | Latest reading, overwritten on every frame via `HSET` |

## Setup

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Redis (Docker)

```bash
docker run -d --name redis -p 6379:6379 redis
```

### 3. Configure (optional)

Edit `backend/.env` if you need to override defaults:

```dotenv
SERIAL_PORT=AUTO          # or e.g. /dev/tty.usbmodem1234
SERIAL_BAUD=115200
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_STREAM_KEY=sensor:stream
REDIS_LATEST_KEY=sensor:latest
REDIS_STREAM_MAXLEN=50000
```

### 4. Connect the board and run

```bash
python main.py
```

The app will auto-detect the NUCLEO board by USB VID (`0x0483`). If detection fails, set `SERIAL_PORT` explicitly in `.env`.

## Verify in Redis CLI

```bash
docker exec -it redis redis-cli

# Check stream length
XLEN sensor:stream

# Read last 5 entries
XREVRANGE sensor:stream + - COUNT 5

# Check latest snapshot
HGETALL sensor:latest
```

## Fields

| Field | Type | Unit |
|---|---|---|
| `timestamp` | string | HH:MM:SS.hh |
| `acc_x_mg` / `y` / `z` | int | mg |
| `gyr_x_mdps` / `y` / `z` | int | mdps |
| `mag_x_mgauss` / `y` / `z` | int | mgauss |
| `press_hpa` | float | hPa |
| `roll_deg` / `pitch_deg` / `yaw_deg` | float | degrees |
