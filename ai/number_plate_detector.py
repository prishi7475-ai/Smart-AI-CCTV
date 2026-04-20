import cv2
from ultralytics import YOLO

# Load YOLOv8 number plate model
# Use a pretrained plate model (you can replace with your own)
model = YOLO("yolov8n.pt")  # vehicle detection base

def detect_number_plates(frame):
    results = model(frame, conf=0.4)
    plates = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            # crude filter (vehicle/plate region)
            if label in ["car", "motorcycle", "bus", "truck"]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plates.append((x1, y1, x2-x1, y2-y1))

    return plates
