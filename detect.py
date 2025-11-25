import subprocess
import time
from pathlib import Path
from datetime import datetime
from gpiozero import MotionSensor, LED
from ultralytics import YOLO
import cv2
import socket
import sys

# set to True for farm testing (saves images in a separate folder)
FARM_MODE = True

print("Starting detect.py...")

# ====== CONFIG ======
# photo storage
if not FARM_MODE:
    SAVE_DIR = Path("/home/rpi/Desktop/ECE449/photos")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
else:
    ALLPHOTOS_DIR = Path("/home/rpi/Desktop/ECE449/testing-photos")
    ANNOTATED_DIR = ALLPHOTOS_DIR / "annotated"
    ALLPHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

RPICAM_CMD = "rpicam-jpeg"
MODEL_PATH = "/home/rpi/Desktop/ECE449/yolov3-tinyu.pt" # pre-trained YOLOv3 model

# Wifi ping
#ESP32_IP = "192.168.68.150"  # Deter ESP32 IP address for wifi ping
#PORT = 4210                  # must match ESP32 code
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# YOLO model
CONF = 0.25
IMGSZ = 416
DEVICE = "cpu"
model = YOLO(MODEL_PATH)

# Define GPIO pins for three PIR sensors and LED strip
pir0 = MotionSensor(26)
pir1 = MotionSensor(20)
pir2 = MotionSensor(21)
ledstrip = LED(16)


# ====== HELPER FUNCTIONS ======

# function to send message to deter ESP32 via wifi
def get_wlan0_ip():
    # Placeholder: In a real system, you'd use 'socket.gethostbyname(socket.gethostname())'
    # or an external library/command to reliably get the wlan0 IP.
    # For now, let's assume the router is .1 and we're looking for the broadcast source IP.
    
    # A reliable way on a Pi is to look up the IP of the wlan0 interface.
    # Let's use a try-catch and rely on the IP being in the range 192.168.68.X
    try:
        # Create a temporary socket to determine the local IP used for external communication
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.68.1", 1)) # Connect to the router/gateway on the network
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        print("Warning: Could not automatically determine local IP. Using 0.0.0.0.")
        return '0.0.0.0' # Fail-safe


def sendWiFi():
    ESP_IP = "192.168.68.255"
    PORT = 5005
    cmd = sys.argv[1] if len(sys.argv) > 1 else "D3"
    local_source_ip = get_wlan0_ip() # <-- NEW: Get the source IP

    print("Attempting to send WiFi command...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # *** CRITICAL FIX: Explicitly bind the socket to the local Wi-Fi interface's IP ***
        sock.bind((local_source_ip, 0)) # 0 means use any available port

        sock.sendto(cmd.encode(), (ESP_IP, PORT))
        sock.close()
        print(f"WiFi broadcast '{cmd}' sent from {local_source_ip} to {ESP_IP}")
        
    except Exception as e:
        # The script is crashing here. This print statement will now show you the error!
        print(f"FATAL: Failed to send WiFi, CRASH ERROR: {e}")
        # To prevent silent crashing in service mode, you MUST have this catch block!


# function to determine if lights are needed for night images (after 5pm or before 9am)
def is_night_time():
    hour = datetime.now().hour
    return hour >= 17 or hour < 9   # returns boolean


# function to capture image from specified camera
def capture_image(source: str, camera_num):
    print(f"Capturing image: (camera {camera_num})")
    # image filepath
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source}_{timestamp}.jpg"
    if not FARM_MODE:
        out_path = SAVE_DIR / filename
    else:
        out_path = ALLPHOTOS_DIR / filename
    
    # capture image from specified camera + silence sensor output
    try:
        subprocess.run(
            [RPICAM_CMD, "--camera", camera_num, "-o", str(out_path)], 
            check=True,
            stdout=subprocess.DEVNULL,  # Silences standard output
            stderr=subprocess.DEVNULL   # Silences errors/warnings (camera debug info)
        )
        print(f"Image captured: {out_path}")
        return out_path
    except subprocess.CalledProcessError as e:
        print(f"Capture failed: {e}")
        return None


# function to run YOLO on image and save annotated result
def run_yolo_and_save(image_path: Path):
    print(f"Running YOLO on {image_path}")
    # run YOLO model and generate annotated image with bounding boxes
    results = model.predict(source=str(image_path), imgsz=IMGSZ, conf=CONF, device=DEVICE, verbose=False)
    r = results[0]
    annotated = r.plot()
    
    # image filepath
    if not FARM_MODE:
        det_path = image_path.with_name(image_path.stem + "-det.jpg")
    else:
        det_filename = image_path.stem + "-det.jpg"
        det_path = ANNOTATED_DIR / det_filename
    cv2.imwrite(str(det_path), annotated)
    print(f"Annotated image saved: {det_path}")
   
    # extract detected classes + confidence scores
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
    return detected_classes


# ===== MAIN LOOP ======

# possible target classes from pre-trained YOLOv3 model
TARGET_CLASSES = {"teddy bear", "groundhog", "raccoon", "squirrel", "cat", "elephant", "cow", "rat", 
                  "otter", "dog", "mouse", "horse", "sheep", "bear", "bird", "zebra", "giraffe", "banana"}

print("PIR Motion sensors active (GPIO 20, 21, 26). Lights on GPIO 27.")

# main detect loop: detect motion from PIR sensor, capture image from corresponding camera, 
# run YOLO, send wifi ping to deter if target animal detected
while True:
    if pir0.motion_detected:
        print("Motion detected on PIR 0 (GPIO 26)")
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
                sendWiFi()
                print("DETER sent. pir0/cam0\n")
        pir0.wait_for_no_motion()

    if pir1.motion_detected:
        print("Motion detected on PIR 1 (GPIO 20)")
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
                sendWiFi()
                print("DETER sent. pir1/cam1\n")
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 2 (GPIO 21)")
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
                sendWiFi()
                print("DETER sent. pir2/cam2\n")
        pir2.wait_for_no_motion()

    time.sleep(0.1)