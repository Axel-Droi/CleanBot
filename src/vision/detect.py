#!/usr/bin/env python3
"""
Entry point for live trash detection.
Usage: python src/vision/detect.py --weights models/cleanbot.pt --source 0 --show
"""
import argparse
import cv2
from src.vision.detector import TrashDetector, CLASS_COLORS


def draw(frame, detections):
    for d in detections:
        x1, y1, x2, y2 = map(int, d.bbox)
        color = CLASS_COLORS.get(d.class_name, (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"{d.class_name} {d.confidence:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return frame


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0", help="Camera index or video file path")
    parser.add_argument("--weights", required=True, help="Path to .pt weights file")
    parser.add_argument("--conf", type=float, default=0.5)
    parser.add_argument("--device", default="cpu", help="cpu | cuda | 0")
    parser.add_argument("--show", action="store_true", help="Show live preview window")
    args = parser.parse_args()

    detector = TrashDetector(args.weights, conf_threshold=args.conf, device=args.device)

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open source: {args.source}")

    print(f"Running CleanBot detector | weights={args.weights} conf={args.conf}")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            detections = detector.detect(frame)
            for d in detections:
                print(f"  {d.class_name:10s} conf={d.confidence:.2f} bbox={tuple(map(int, d.bbox))}")
            if args.show:
                cv2.imshow("CleanBot", draw(frame, detections))
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
