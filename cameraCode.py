import time
import subprocess
from pathlib import Path
from datetime import datetime
from gpiozero import MotionSensor
from ultralytics import YOLO

# ====== CONFIG ======
SAVE_DIR = Path("/home/rpi/Desktop/ECE449/photos")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
RPICAM_CMD = "rpicam-jpeg"  # full path if needed, e.g. "/usr/bin/rpicam-jpeg"
MODEL_PATH = "/home/rpi/Desktop/ECE449/yolov3-tinyu.pt"
# ====================

#model setup
CONF = 0.25
IMGSZ = 416                 # v3-tiny usually runs well at 320 or 416
DEVICE = "cpu"

# Define three PIR sensors
pir1 = MotionSensor(20)
pir2 = MotionSensor(21)
pir3 = MotionSensor(26)

print("Motion sensors active (GPIO 20, 21, 26). Waiting for motion...")

# load once
model = YOLO(MODEL_PATH)

def capture_image(source: str):
    """Capture image with timestamp and sensor label."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source}_{timestamp}.jpg"
    out_path = SAVE_DIR / filename

    # print(f"Capturing image: {out_path}", camera_num)  # for 2 working cameras
    print(f"Capturing image: {out_path}")
    try:
        # subprocess.run([RPICAM_CMD, "--camera", camera_num, "-o", str(out_path)], check=True)     # for 2 working cameras
        subprocess.run([RPICAM_CMD, "--camera", "1", "-o", str(out_path)], check=True)
        print(f"Saved: {out_path}")
        return out_path
    except subprocess.CalledProcessError as e:
        print(f"Capture failed: {e}")
        return None

def run_yolo_and_save(image_path: Path):
    print(f"YOLO on {image_path}")
    results = model.predict(
        source=str(image_path),
        imgsz=IMGSZ,
        conf=CONF,
        device=DEVICE,
        verbose=False
    )
    r = results[0]
    # Save annotated image next to the original
    annotated = r.plot()  # numpy array (BGR)
    det_path = image_path.with_name(image_path.stem + "-det.jpg")
    import cv2
    cv2.imwrite(str(det_path), annotated)

    # Console summary
    boxes = getattr(r, "boxes", None)
    if boxes is not None and len(boxes) > 0:
        names = r.names
        cls_ids = boxes.cls.tolist()
        confs = boxes.conf.tolist()
        summary = ", ".join(f"{names[int(i)]}:{c:.2f}" for i, c in zip(cls_ids, confs))
        print(f"Detections: {summary}")
    else:
        print("Detections: none")
    print(f"Annotated saved: {det_path}")

# Main loop
while True:
    if pir1.motion_detected:
        print("Motion detected on PIR 1 (GPIO 20)")
        p = capture_image("pir1")
        # capture_image("pir1", "1")  # with 2 working cameras
        if p:
            run_yolo_and_save(p)
        pir1.wait_for_no_motion()

    if pir2.motion_detected:
        print("Motion detected on PIR 2 (GPIO 21)")
        p = capture_image("pir2")
        # capture_image("pir2", "1")    # with 2 working cameras
        if p:
            run_yolo_and_save(p)
        pir2.wait_for_no_motion()

    if pir3.motion_detected:
        print("Motion detected on PIR 3 (GPIO 26)")
        p = capture_image("pir3")
        # capture_image("pir3", "0")    # with 2 working cameras
        if p:
            run_yolo_and_save(p)
        pir3.wait_for_no_motion()

    time.sleep(0.1)