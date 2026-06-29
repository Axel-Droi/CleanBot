#!/usr/bin/env python3
"""
Train YOLOv11-Nano for CleanBot trash detection.

Target: mAP@0.5 >= 0.95 on 4 classes (plastic, metal, paper, bio_waste)
Split:  70% train / 30% val (set in prepare_data.py)

Usage:
  # Standard training (Jetson Nano target)
  python training/train.py

  # Resume from checkpoint
  python training/train.py --resume runs/train/cleanbot/weights/last.pt

  # Use a larger model if nano struggles to hit 95% mAP
  python training/train.py --model yolo11s.pt
"""
import argparse
from pathlib import Path

from ultralytics import YOLO

REPO_ROOT  = Path(__file__).resolve().parents[1]
DATA_YAML  = REPO_ROOT / "data" / "dataset.yaml"
MODELS_DIR = REPO_ROOT / "models"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",   default="yolo11n.pt",
                        help="Base weights (yolo11n.pt | yolo11s.pt | yolo11m.pt)")
    parser.add_argument("--epochs",  type=int, default=150)
    parser.add_argument("--imgsz",   type=int, default=640)
    parser.add_argument("--batch",   type=int, default=16,
                        help="Batch size — reduce to 8 if you hit OOM")
    parser.add_argument("--device",  default="0",
                        help="cuda device index, or 'cpu'")
    parser.add_argument("--resume",  default="",
                        help="Path to last.pt to resume training")
    parser.add_argument("--name",    default="cleanbot",
                        help="Run name under runs/train/")
    args = parser.parse_args()

    if not DATA_YAML.exists():
        raise FileNotFoundError(
            f"dataset.yaml not found at {DATA_YAML}\n"
            "Run: python training/prepare_data.py"
        )

    if args.resume:
        model = YOLO(args.resume)
        print(f"Resuming from {args.resume}")
    else:
        model = YOLO(args.model)
        print(f"Starting fresh training with {args.model}")

    results = model.train(
        data=str(DATA_YAML),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        name=args.name,
        project="runs/train",
        patience=30,          # early stopping if no improvement for 30 epochs
        save=True,
        save_period=10,       # checkpoint every 10 epochs

        # Augmentation — helps generalize across lighting, environments
        hsv_h=0.015,          # hue shift
        hsv_s=0.7,            # saturation shift
        hsv_v=0.4,            # value/brightness shift
        degrees=10.0,         # rotation
        translate=0.1,
        scale=0.5,
        flipud=0.1,
        fliplr=0.5,
        mosaic=1.0,           # mosaic augmentation (critical for small objects)
        mixup=0.1,
        copy_paste=0.1,

        # Optimizer
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,             # final lr = lr0 * lrf
        weight_decay=0.0005,
        warmup_epochs=3,

        # Logging
        plots=True,
        verbose=True,
    )

    # Copy best weights to models/
    MODELS_DIR.mkdir(exist_ok=True)
    best_src = Path(f"runs/train/{args.name}/weights/best.pt")
    if best_src.exists():
        import shutil
        dest = MODELS_DIR / "cleanbot_nano.pt"
        shutil.copy2(best_src, dest)
        print(f"\nBest weights saved → {dest}")

    # Print final metrics
    try:
        metrics  = results.results_dict
        map50    = metrics.get("metrics/mAP50(B)", 0)
        map50_95 = metrics.get("metrics/mAP50-95(B)", 0)
    except AttributeError:
        # Older ultralytics versions don't expose results_dict on the return value
        try:
            map50    = results.trainer.validator.metrics.box.map50
            map50_95 = results.trainer.validator.metrics.box.map
        except Exception:
            map50 = map50_95 = 0.0
    print(f"\nFinal metrics:")
    print(f"  mAP@0.50      = {map50:.4f}  (target: 0.9500)")
    print(f"  mAP@0.50:0.95 = {map50_95:.4f}")

    if map50 < 0.95:
        print("\nNote: mAP@0.5 is below 0.95 target. Options to improve:")
        print("  1. Add more data (--rf-key in download_data.py to pull Roboflow datasets)")
        print("  2. Use a larger model: --model yolo11s.pt")
        print("  3. Train longer: --epochs 200")
        print("  4. Resume from checkpoint: --resume runs/train/cleanbot/weights/last.pt")
    else:
        print("\n95% accuracy target achieved.")


if __name__ == "__main__":
    main()
