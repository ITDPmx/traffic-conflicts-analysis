from ultralytics import YOLO

# Configure the tracking parameters and run the tracker
model = YOLO('yolov8l.pt')
results = model.track(source="cruce.mp4", conf=0.3, iou=0.5)
