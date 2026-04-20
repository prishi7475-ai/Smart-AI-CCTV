from ultralytics import YOLO

model = YOLO("models/yolov8n.pt")

def detect_objects(frame):
    results = model(frame)
    objects = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            objects.append((label, x1, y1, x2, y2))

    return objects
