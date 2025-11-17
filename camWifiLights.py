import subprocess
import time
from pathlib import Path
from datetime import datetime
from gpiozero import MotionSensor, LED
from ultralytics import YOLO
import cv2
import socket

# CONFIG
# model + photo storage
SAVE_DIR = Path("/home/rpi/Desktop/ECE449/photos")  
# SAVE_DIR = Path("/home/rpi/Desktop/ECE449/testing-photos")  # uncomment for farm testing
SAVE_DIR.mkdir(parents=True, exist_ok=True)
RPICAM_CMD = "rpicam-jpeg"
MODEL_PATH = "/home/rpi/Desktop/ECE449/yolov3-tinyu.pt" # pre-trained model

# wifi ping
ESP32_IP = "192.168.68.150"  # Deter ESP32 IP address for wifi ping
PORT = 4210                  # must match ESP32 code
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# model setup
CONF = 0.25
IMGSZ = 416
DEVICE = "cpu"

# Define three PIR sensors
pir0 = MotionSensor(26)
pir1 = MotionSensor(21)
pir2 = MotionSensor(20)

# Define light/LED strip
ledstrip = LED(16)

# Load YOLO model once
model = YOLO(MODEL_PATH)

print("PIR Motion sensors active (GPIO 20, 21, 26). Lights on GPIO 27.")

# function to send message across wifi to Deter ESP32
def sendWiFi(message: str):
    data = message.encode()
    sock.sendto(data, (ESP32_IP, PORT))
    print(f"Sent: {message}")

# function to check time to determine if lights are needed
def is_night_time():
    """Return True if current time is after 5 PM or before 9 AM."""
    hour = datetime.now().hour
    return hour >= 17 or hour < 9

# function to capture image from specified camera
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

# function to run YOLO on image and save annotated result
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

# possible target classes from pre-trained YOLOv3 model
TARGET_CLASSES = {"teddy bear", "groundhog", "raccoon", "squirrel", "cat", 
                  "elephant", "cow", "rat", "otter", "dog", "mouse", "horse", "sheep",
                  "bear", "bird", "zebra", "giraffe", 
                  "banana"}

# MAIN LOOP
# detect motion from PIR sensor, capture image from corresponding camera, 
# run YOLO, send wifi ping to deter if target detected
while True:
    if pir0.motion_detected:
        print("Motion detected on PIR 1 (GPIO 20)")
        # check if night time for lights
        if is_night_time():
            ledstrip.on()
            time.sleep(0.2)  # small delay for light to illuminate scene
        p = capture_image("pir0", "0")
        ledstrip.off()
        # run YOLO to check for target animal
        if p:
            detected = run_yolo_and_save(p)
            if any(obj in TARGET_CLASSES for obj in detected):
                sendWiFi("DETER")
                print("DETER sent. pir0/cam0")
        pir0.wait_for_no_motion()

    if pir1.motion_detected:
        print("Motion detected on PIR 2 (GPIO 21)")
        # check if night time for lights
        if is_night_time():
            ledstrip.on()
            time.sleep(0.2)
        p = capture_image("pir1", "1")
        ledstrip.off()
        # run YOLO to check for target animal
        if p:
            detected = run_yolo_and_save(p)
            if any(obj in TARGET_CLASSES for obj in detected):
                sendWiFi("DETER")
                print("DETER sent. pir1/cam1")
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 3 (GPIO 26)")
        # check if night time for lights
        if is_night_time():
            ledstrip.on()
            time.sleep(0.2)
        p = capture_image("pir2", "2")
        ledstrip.off()
        # run YOLO to check for target animal
        if p:
            detected = run_yolo_and_save(p)
            if any(obj in TARGET_CLASSES for obj in detected):
                sendWiFi("DETER")
                print("DETER sent. pir2/cam2")
        pir2.wait_for_no_motion()

    time.sleep(0.1)
