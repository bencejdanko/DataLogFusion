import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# Thread-safe buffer for the latest camera frame
latest_frame = None
frame_lock = threading.Lock()
last_frame_time = 0

def generate_placeholder_frame(status="STANDBY", detail="Waiting for motion..."):
    try:
        import cv2
        import numpy as np
        # Create a 640x360 dark image (16:9 ratio)
        img = np.zeros((360, 640, 3), dtype=np.uint8)
        
        # Draw a subtle dark grid pattern for high tech look
        for x in range(0, 640, 40):
            cv2.line(img, (x, 0), (x, 360), (15, 15, 20), 1)
        for y in range(0, 360, 40):
            cv2.line(img, (0, y), (640, y), (15, 15, 20), 1)
            
        # Draw a glowing border (dark blue)
        cv2.rectangle(img, (10, 10), (630, 350), (100, 50, 0), 2)
        
        # Pulsing target indicator
        pulse = int(128 + 127 * np.sin(time.time() * 4))
        pulse = max(0, min(255, pulse))
        
        if status == "STANDBY":
            color = (0, pulse // 2, pulse) # Orange/Yellow pulse (BGR: blue=0, green=pulse/2, red=pulse)
            text_color = (0, 165, 255)
        else:
            color = (0, pulse, 0) # Green pulse
            text_color = (0, 255, 0)
            
        cv2.circle(img, (40, 40), 8, color, -1)
        cv2.putText(img, "LIVE", (60, 47), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Main title
        cv2.putText(img, "SENTRY MONITOR SYSTEM", (140, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Status text
        cv2.putText(img, f"STATUS: {status}", (140, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
        
        # Detail text
        cv2.putText(img, detail, (140, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
        
        # Encode to JPEG
        _, jpeg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return jpeg.tobytes()
    except Exception:
        # Minimal 1x1 black JPEG fallback
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\x92\xa2\x16C\xe1\xf1%4S\xb2\xc2\xd2\x09\n\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x93\x94\x95\x96\x97\x98\x99\x9a\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xff\xd9'

class SentryHubHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global latest_frame, last_frame_time
        if self.path == '/feed':
            # Read incoming raw JPEG bytes from the Pi
            content_length = int(self.headers['Content-Length'])
            frame_data = self.rfile.read(content_length)
            
            with frame_lock:
                # Check if headers indicate raw frame format from QNX
                width_hdr = self.headers.get('X-Width')
                height_hdr = self.headers.get('X-Height')
                fmt_hdr = self.headers.get('X-Format')
                
                if width_hdr and height_hdr and fmt_hdr:
                    try:
                        import numpy as np
                        import cv2
                        
                        width = int(width_hdr)
                        height = int(height_hdr)
                        fmt = int(fmt_hdr)
                        
                        raw_arr = np.frombuffer(frame_data, dtype=np.uint8)
                        
                        # Handle different frame buffer formats
                        converted = False
                        if len(raw_arr) == width * height * 4: # BGR8888 or RGB8888
                            img = raw_arr.reshape((height, width, 4))
                            # Most QNX camera feeds default to BGR8888 (fmt=0) or RGB8888 (fmt=1)
                            # Convert BGRx/RGBx to 3-channel BGR for JPEG compression
                            bgr_img = img[:, :, :3]
                            if fmt == 1: # RGB8888 -> swap red and blue channels
                                bgr_img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                            _, jpeg = cv2.imencode('.jpg', bgr_img, [cv2.IMWRITE_JPEG_QUALITY, 80])
                            latest_frame = jpeg.tobytes()
                            converted = True
                        elif len(raw_arr) == int(width * height * 1.5): # NV12 (YUV420 semi-planar)
                            yuv = raw_arr.reshape((int(height * 1.5), width))
                            bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
                            _, jpeg = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
                            latest_frame = jpeg.tobytes()
                            converted = True
                        elif fmt == 14: # CAMERA_FRAMETYPE_YCBYCR (YUV 4:2:2 packed / YUYV / YUY2)
                            yuv = raw_arr.reshape((height, width, 2))
                            bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_YUY2)
                            _, jpeg = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
                            latest_frame = jpeg.tobytes()
                            converted = True
                        
                        if converted:
                            print(f"[Server] Frame successfully converted: format={fmt}, res={width}x{height}, jpeg_size={len(latest_frame)} bytes")
                        else:
                            # Unsupported buffer layout fallback
                            print(f"[Server] Unsupported buffer layout fallback: fmt={fmt}, array_size={len(raw_arr)} bytes (expected {width}x{height})")
                            latest_frame = frame_data
                    except Exception as e:
                        print(f"Error converting raw frame: {e}")
                        latest_frame = frame_data
                else:
                    # Direct JPEG fallback
                    print(f"[Server] Direct JPEG fallback: size={len(frame_data)} bytes")
                    latest_frame = frame_data
                    
                last_frame_time = time.time()
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            
    def do_GET(self):
        global latest_frame, last_frame_time
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('X-Accel-Buffering', 'no')
            self.end_headers()
            
            try:
                while True:
                    # If no frame received in the last 5 seconds, stream standby placeholder
                    if time.time() - last_frame_time > 5.0:
                        frame = generate_placeholder_frame("STANDBY", "Waiting for motion trigger...")
                    else:
                        with frame_lock:
                            frame = latest_frame
                        if not frame:
                            frame = generate_placeholder_frame("STANDBY", "Initializing stream...")
                    
                    self.wfile.write(b'--frame\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame)))
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')
                    self.send_header('X-Accel-Buffering', 'no')
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                    self.wfile.flush() # Force transmission of this frame immediately
                    
                    time.sleep(0.05) # Stream at ~20 FPS
            except Exception:
                pass
        else:
            self.send_response(404)
            self.end_headers()

def main():
    # Bind to 0.0.0.0 so the Pi on the local network can hit it
    server = ThreadingHTTPServer(('0.0.0.0', 8080), SentryHubHandler)
    print("Sentry Hub broadcasting at: http://localhost:8080/stream.mjpg")
    print("Point your Cloudflare Tunnel to this port.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Broadcast Server.")

if __name__ == "__main__":
    main()
