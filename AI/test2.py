import os
from ultralytics import YOLO

print("Script started")
print("Saving to:", os.getcwd())

model = YOLO('yolov8n.pt')
results = model('https://ultralytics.com/images/bus.jpg')
results[0].save(filename='result.jpg')
print(results[0].boxes)