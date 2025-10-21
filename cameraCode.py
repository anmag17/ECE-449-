import time
import subprocess
from pathlib import Path
from datetime import datetime
from gpiozero import MotionSensor

# ====== CONFIG ======
SAVE_DIR = Path("/home/rpi/Desktop/ECE449  ")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
RPICAM_CMD = "rpicam-jpeg"  # full path if needed, e.g. "/usr/bin/rpicam-jpeg"
# ====================

# Define three PIR sensors
pir1 = MotionSensor(4)
pir2 = MotionSensor(5)
pir3 = MotionSensor(6)

print("Motion sensors active (GPIO 4, 5, 6). Waiting for motion...")

def capture_image(source: str):
    """Capture image with timestamp and sensor label."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source}_{timestamp}.jpg"
    out_path = SAVE_DIR / filename

    print(f"📸 Capturing image: {out_path}")
    try:
        subprocess.run([RPICAM_CMD, "-o", str(out_path)], check=True)
        print(f"Saved: {out_path}")
    except subprocess.CalledProcessError as e:
        print(f"Capture failed: {e}")

# Main loop
while True:
    if pir1.motion_detected:
        print("Motion detected on PIR 1 (GPIO 4)")
        capture_image("pir1")
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 2 (GPIO 5)")
        capture_image("pir2")
        pir2.wait_for_no_motion()

    if pir3.motion_detected:
        print("Motion detected on PIR 3 (GPIO 6)")
        capture_image("pir3")
        pir3.wait_for_no_motion()

    time.sleep(0.1)