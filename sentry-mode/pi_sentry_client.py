import rpi_gpio as GPIO
import time
import urllib.request
import subprocess
import os

import threading

# Configuration
SIG_PIN = 21
LED_PIN = 20
# Replace with your laptop's local IP address on your network
LAPTOP_URL = "http://172.20.10.4:8080/feed" 
STREAM_TIMEOUT = 10 # Keep streaming 10 seconds after last motion detection
DOWNSAMPLE_FACTOR = 2 # Factor to downsample raw YCBYCR frame (1 to disable)
POST_TIMEOUT = 5.0 # Timeout in seconds for HTTP upload POST requests

# C Capture Utility paths
BINARY_PATH = "./camera_capture"
DUMP_DIR = "/tmp"
RAW_FILE = "/tmp/frame0.raw"

# Shared state
last_trigger_time = 0
last_attempt_time = 0  # Cooldown tracker
streaming = False
stream_lock = threading.Lock()

def downsample_ycbycr(frame_bytes, width, height, factor=2):
    """
    Downsamples a YCBYCR (YUYV) frame by the given factor.
    YCBYCR is a packed YUV 4:2:2 format: 4 bytes per 2 pixels (Y1, U, Y2, V).
    A row has width * 2 bytes.
    We take every 'factor' rows.
    In each row, we take every 'factor' blocks of 4 bytes.
    """
    if factor <= 1:
        return frame_bytes, width, height

    row_stride = width * 2
    new_width = width // factor
    # Ensure new_width is even (YCBYCR needs even width since 2 pixels per block)
    if new_width % 2 != 0:
        new_width = (new_width // 2) * 2
        
    new_height = height // factor
    
    block_step = 4 * factor
    bytes_per_row_to_keep = (new_width // 2) * 4  # Each 2 pixels is a 4-byte block
    
    out_rows = []
    for r in range(0, height, factor):
        if len(out_rows) >= new_height:
            break
        row_start = r * row_stride
        row_data = frame_bytes[row_start : row_start + row_stride]
        
        # Extract the blocks
        row_chunks = [row_data[i : i + 4] for i in range(0, len(row_data), block_step)]
        row_bytes = b"".join(row_chunks)[:bytes_per_row_to_keep]
        out_rows.append(row_bytes)
        
    downsampled_bytes = b"".join(out_rows)
    return downsampled_bytes, new_width, new_height

def camera_stream_worker():
    global streaming
    print("[Camera] Background thread started. Streaming using QNX camera_capture C utility...")
    
    proc = None
    try:
        # Spawn the persistent C capture utility in stream mode (-s)
        proc = subprocess.Popen(
            [BINARY_PATH, "-s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
        
        # Read the metadata from stderr (should be printed on start)
        meta_line = None
        while proc.poll() is None:
            line = proc.stderr.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                time.sleep(0.01)
                continue
            if "[Camera] Meta:" in line:
                meta_line = line
                break
            else:
                print(f"[Camera C-API Msg] {line}")
        
        if not meta_line:
            if proc.poll() is not None:
                stderr_content = proc.stderr.read().decode('utf-8', errors='ignore')
                print(f"[Camera] Failed to start. Process exited with {proc.returncode}. Stderr: {stderr_content}")
            else:
                print("[Camera] Failed to receive metadata from camera capture process.")
            streaming = False
            return

        parts = meta_line.split()
        dims = parts[2].split("x")
        width = int(dims[0])
        height = int(dims[1])
        fmt = int(parts[3].split("=")[1])
        stride = int(parts[4].split("=")[1])
        size = int(parts[5].split("=")[1])
        
        print(f"[Camera] Streaming initialized: {width}x{height} fmt={fmt} size={size}")

        while True:
            with stream_lock:
                is_active = (time.time() - last_trigger_time < STREAM_TIMEOUT)
                if not is_active:
                    print("[Camera] Timeout reached. Stopping C capture stream...")
                    streaming = False
                    break
            
            try:
                # Read exactly `size` bytes from the process's stdout
                frame_bytes = b""
                while len(frame_bytes) < size:
                    chunk = proc.stdout.read(size - len(frame_bytes))
                    if not chunk:
                        raise BrokenPipeError("Camera capture stdout closed prematurely")
                    frame_bytes += chunk
                
                # Apply downsampling if requested and supported
                curr_width, curr_height, curr_stride = width, height, stride
                curr_frame_bytes = frame_bytes
                
                if fmt == 14 and DOWNSAMPLE_FACTOR > 1:
                    curr_frame_bytes, new_w, new_h = downsample_ycbycr(frame_bytes, width, height, DOWNSAMPLE_FACTOR)
                    curr_width = new_w
                    curr_height = new_h
                    curr_stride = new_w * 2

                # POST raw pixels directly to laptop with metadata headers
                req = urllib.request.Request(
                    LAPTOP_URL, 
                    data=curr_frame_bytes, 
                    headers={
                        'Content-Type': 'application/octet-stream',
                        'X-Width': str(curr_width),
                        'X-Height': str(curr_height),
                        'X-Format': str(fmt),
                        'X-Stride': str(curr_stride)
                    }
                )
                with urllib.request.urlopen(req, timeout=POST_TIMEOUT) as response:
                    response.read()
            except Exception as e:
                print("[Camera] Capture or transfer failed:", e)
                if isinstance(e, (BrokenPipeError, ConnectionResetError)) or (proc.poll() is not None):
                    print("[Camera] Subprocess died. Stopping camera stream worker.")
                    break
                time.sleep(1.0)
            
            time.sleep(0.01)
    except Exception as e:
        print("[Camera] Stream worker exception:", e)
    finally:
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=1.0)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        print("[Camera] Background thread finished.")

def main():
    global last_trigger_time, last_attempt_time, streaming
    GPIO.setup(SIG_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PIN, GPIO.OUT)
    
    print("Pi Sentry monitoring IR sensor...")
    try:
        while True:
            # Active-low detection: 0 = obstacle detected
            if GPIO.input(SIG_PIN) == 0:
                GPIO.output(LED_PIN, GPIO.HIGH)
                
                with stream_lock:
                    last_trigger_time = time.time()
                    current_time = time.time()
                    
                    # Only try to spawn the camera thread if not already running AND after a 10s cooldown
                    if not streaming and (current_time - last_attempt_time > 10.0):
                        print("[Pi] Trigger detected! Starting background camera thread...")
                        streaming = True
                        last_attempt_time = current_time
                        t = threading.Thread(target=camera_stream_worker, daemon=True)
                        t.start()
            else:
                GPIO.output(LED_PIN, GPIO.LOW)
                
            time.sleep(0.05) # Poll sensor every 50ms
    except KeyboardInterrupt:
        print("\nStopping Pi client.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
