from ultralytics import YOLO

# Load model
model = YOLO("yolov8n.pt")  # Replace with your custom model if you have one

# Load and run on an image
image_path = "bus.jpg"
results = model(image_path)

# Get the detection results
detections = results[0]
class_names = model.names  # class index to name mapping

# Check if any boxes are detected
if detections.boxes is not None and len(detections.boxes.data) > 0:
    print("\n ANALYSIS REPORT:\n")
    
    for box in detections.boxes.data:
        class_id = int(box[5])
        confidence = float(box[4])
        label = class_names[class_id]

        # Define basic trash-like items (expand as needed)
        trash_keywords = ["bottle", "can", "cup", "trash", "bag", "plastic", "wrapper"]

        if any(word in label.lower() for word in trash_keywords):
            print(f" TRASH DETECTED → {label} ({confidence:.2f})")
        else:
            print(f" NOT TRASH → {label} ({confidence:.2f})")
else:
    print("⚠️  No objects detected in the image.")
