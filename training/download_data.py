#!/usr/bin/env python3
"""
Download trash detection datasets for CleanBot training.

Datasets pulled:
  1. TACO  — Trash Annotations in Context (Proença & Simões, 2020)
             ~1,500 real outdoor litter images, COCO format, 60 categories
  2. Roboflow Garbage Detection — ~2,500 images, pre-annotated in YOLO format
  3. Roboflow Litter Detection  — ~1,200 street/park litter images
  4. Open Images v7 (litter subset) — large-scale Google-quality images

Usage:
  # TACO only (no API key needed):
  python training/download_data.py --taco

  # TACO + Roboflow datasets (requires free Roboflow API key):
  python training/download_data.py --taco --roboflow --rf-key YOUR_KEY

  # All datasets:
  python training/download_data.py --all --rf-key YOUR_KEY
"""
import argparse
import subprocess
import sys
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parents[3] / "data" / "raw"


def run(cmd: list[str]):
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def download_taco():
    dest = DATA_ROOT / "taco"
    dest.mkdir(parents=True, exist_ok=True)

    taco_repo = dest / "TACO"
    if not taco_repo.exists():
        run(["git", "clone", "--depth", "1",
             "https://github.com/pedropro/TACO.git", str(taco_repo)])

    print("\nDownloading TACO images from Flickr (this takes ~15 min)...")
    print("Note: some Flickr URLs may 404 — TACO will skip those automatically.")
    run([sys.executable, str(taco_repo / "download.py"), "-p", str(dest)])
    print(f"TACO downloaded → {dest}")


def download_roboflow(api_key: str):
    """
    Downloads two Roboflow Universe datasets in YOLO format.

    Dataset slugs:
      - material-identification/garbage-classification-3   (~2,500 imgs)
      - roboflow-100/lifelike-litter                       (~1,200 imgs)

    Both are free on Roboflow Universe (sign up at roboflow.com for a free API key).
    """
    try:
        from roboflow import Roboflow
    except ImportError:
        run([sys.executable, "-m", "pip", "install", "roboflow", "-q"])
        from roboflow import Roboflow

    rf = Roboflow(api_key=api_key)

    # Dataset 1: Garbage Classification / Detection
    dest1 = DATA_ROOT / "roboflow" / "garbage_detection"
    dest1.mkdir(parents=True, exist_ok=True)
    proj1 = rf.workspace("material-identification").project("garbage-classification-3")
    proj1.version(2).download("yolov8", location=str(dest1))
    print(f"Roboflow garbage-detection → {dest1}")

    # Dataset 2: Lifelike Litter (real-world street & park litter)
    dest2 = DATA_ROOT / "roboflow" / "litter_detection"
    dest2.mkdir(parents=True, exist_ok=True)
    proj2 = rf.workspace("roboflow-100").project("lifelike-litter")
    proj2.version(1).download("yolov8", location=str(dest2))
    print(f"Roboflow litter-detection → {dest2}")


def download_open_images():
    """
    Downloads the 'Waste container' class from Open Images v7 via fiftyone.
    Produces ~3,000 images with bounding box annotations.
    """
    try:
        import fiftyone as fo
        import fiftyone.zoo as foz
    except ImportError:
        run([sys.executable, "-m", "pip", "install", "fiftyone", "-q"])
        import fiftyone as fo
        import fiftyone.zoo as foz

    dest = DATA_ROOT / "open_images"
    dest.mkdir(parents=True, exist_ok=True)

    print("Downloading Open Images v7 — Waste container class (~3,000 images)...")
    dataset = foz.load_zoo_dataset(
        "open-images-v7",
        split="train",
        label_types=["detections"],
        classes=["Waste container"],
        max_samples=3000,
        dataset_dir=str(dest),
    )
    print(f"Open Images downloaded → {dest}  ({len(dataset)} samples)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taco", action="store_true", help="Download TACO dataset")
    parser.add_argument("--roboflow", action="store_true", help="Download Roboflow datasets")
    parser.add_argument("--open-images", action="store_true", help="Download Open Images subset")
    parser.add_argument("--all", dest="all_sets", action="store_true",
                        help="Download all datasets (requires --rf-key)")
    parser.add_argument("--rf-key", default="", help="Roboflow API key (free at roboflow.com)")
    args = parser.parse_args()

    if not any([args.taco, args.roboflow, args.open_images, args.all_sets]):
        parser.print_help()
        return

    if args.taco or args.all_sets:
        download_taco()

    if args.roboflow or args.all_sets:
        if not args.rf_key:
            print("ERROR: --rf-key required for Roboflow downloads. "
                  "Get a free key at https://roboflow.com")
            sys.exit(1)
        download_roboflow(args.rf_key)

    if args.open_images or args.all_sets:
        download_open_images()

    print("\nAll requested datasets downloaded.")
    print(f"Raw data location: {DATA_ROOT}")
    print("Next step: python training/prepare_data.py")


if __name__ == "__main__":
    main()
