from pathlib import Path
from dataclasses import dataclass
import numpy as np
from ultralytics import YOLO

CLASSES = ["plastic", "metal", "paper", "bio_waste"]

# BGR colors for visualization
CLASS_COLORS = {
    "plastic":   (0, 165, 255),  # orange
    "metal":     (192, 192, 192),  # silver
    "paper":     (0, 255, 255),  # yellow
    "bio_waste": (0, 180, 0),    # green
}


@dataclass
class Detection:
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 in pixels
    class_id: int
    class_name: str
    confidence: float


class TrashDetector:
    def __init__(self, weights: str | Path, conf_threshold: float = 0.5, device: str = "cpu"):
        self.model = YOLO(str(weights))
        self.conf = conf_threshold
        self.device = device

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self.model(frame, conf=self.conf, device=self.device, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                name = CLASSES[cls] if cls < len(CLASSES) else "unknown"
                detections.append(Detection(
                    bbox=(x1, y1, x2, y2),
                    class_id=cls,
                    class_name=name,
                    confidence=float(box.conf[0]),
                ))
        return detections
