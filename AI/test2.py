from ultralytics import YOLO

print("Starting YOLO test...")

model = YOLO('yolov8n.pt')
print("Model loaded.")

results = model('https://ultralytics.com/images/bus.jpg')
print("Inference done.")

results[0].save(filename='result.jpg')
print("Result saved.")
print(results[0].boxes)