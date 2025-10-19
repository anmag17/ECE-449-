import argparse
from ultralytics import YOLO

p = argparse.ArgumentParser()
p.add_argument("--source", default="bus.jpg")
p.add_argument("--imgsz", type=int, default=640)
p.add_argument("--conf", type=float, default=0.25)
args = p.parse_args()

model = YOLO("yolov3-tinyu.pt")  # COCO-pretrained; auto-downloads
model.predict(source=args.source, imgsz=args.imgsz, conf=args.conf, device="cpu", show=False, save=True, verbose=True)
