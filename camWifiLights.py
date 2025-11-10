import subprocess
import time
from pathlib import Path
from datetime import datetime
from gpiozero import MotionSensor, LED
from ultralytics import YOLO
import cv2
import socket

# ====== CONFIG ======
SAVE_DIR = Path("/home/rpi/Desktop/ECE449/photos")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
RPICAM_CMD = "rpicam-jpeg"
MODEL_PATH = "/home/rpi/Desktop/ECE449/yolov3-tinyu.pt"

ESP32_IP = "192.168.68.150"  # Replace with your ESP32’s IP
PORT = 4210  # must match ESP32 code

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ====================

# model setup
CONF = 0.25
IMGSZ = 416
DEVICE = "cpu"

# Define three PIR sensors
pir1 = MotionSensor(20)
pir2 = MotionSensor(21)
pir3 = MotionSensor(26)

# Define LEDs corresponding to each PIR
led1 = LED(27)
led2 = LED(23)
led3 = LED(24)

print("Motion sensors active (GPIO 20, 21, 26). Lights on GPIO 27, 23, 24.")

# WiFi function
def sendWiFi(message: str):
    data = message.encode()
    sock.sendto(data, (ESP32_IP, PORT))
    print(f"Sent: {message}")

# Load YOLO once
model = YOLO(MODEL_PATH)

def is_night_time():
    """Return True if current time is after 5 PM or before 9 AM."""
    hour = datetime.now().hour
    return hour >= 17 or hour < 9

def capture_image(source: str, camera_num):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source}_{timestamp}.jpg"
    out_path = SAVE_DIR / filename

    print(f"Capturing image: {out_path} (camera {camera_num})")
    try:
        subprocess.run([RPICAM_CMD, "--camera", camera_num, "-o", str(out_path)], check=True)
        print(f"Saved: {out_path}")
        return out_path
    except subprocess.CalledProcessError as e:
        print(f"Capture failed: {e}")
        return None

def run_yolo_and_save(image_path: Path):
    print(f"Running YOLO on {image_path}")
    results = model.predict(source=str(image_path), imgsz=IMGSZ, conf=CONF, device=DEVICE, verbose=False)
    r = results[0]
    annotated = r.plot()
    det_path = image_path.with_name(image_path.stem + "-det.jpg")
    cv2.imwrite(str(det_path), annotated)

    boxes = getattr(r, "boxes", None)
    detected_classes = []

    if boxes is not None and len(boxes) > 0:
        names = r.names
        cls_ids = boxes.cls.tolist()
        confs = boxes.conf.tolist()
        summary = ", ".join(f"{names[int(i)]}:{c:.2f}" for i, c in zip(cls_ids, confs))
        print(f"Detections: {summary}")
        detected_classes = [names[int(i)].lower() for i in cls_ids]
    else:
        print("Detections: none")

    print(f"Annotated saved: {det_path}")
    return detected_classes

TARGET_CLASSES = {"teddy bear", "groundhog", "raccoon", "squirrel"}

# Main loop
while True:
    if pir1.motion_detected:
        print("Motion detected on PIR 1 (GPIO 20)")
        if is_night_time():
            led1.on()
            time.sleep(0.2)  # small delay for light to illuminate scene
        p = capture_image("pir1", "0")
        if p:
            detected = run_yolo_and_save(p)
            if any(obj in TARGET_CLASSES for obj in detected):
                sendWiFi("DETER")
        led1.off()
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 2 (GPIO 21)")
        if is_night_time():
            led2.on()
            time.sleep(0.2)
        p = capture_image("pir2", "1")
        if p:
            detected = run_yolo_and_save(p)
            if any(obj in TARGET_CLASSES for obj in detected):
                sendWiFi("DETER")
        led2.off()
        pir2.wait_for_no_motion()

    if pir3.motion_detected:
        print("Motion detected on PIR 3 (GPIO 26)")
        if is_night_time():
            led3.on()
            time.sleep(0.2)
        p = capture_image("pir3", "2")
        if p:
            detected = run_yolo_and_save(p)
            if any(obj in TARGET_CLASSES for obj in detected):
                sendWiFi("DETER")
        led3.off()
        pir3.wait_for_no_motion()

    time.sleep(0.1)
