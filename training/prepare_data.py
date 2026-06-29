#!/usr/bin/env python3
"""
Prepare the combined CleanBot training dataset.

Steps:
  1. Load TACO COCO annotations + map 60 TACO categories → 4 CleanBot classes
  2. Convert COCO bbox format to YOLO txt format
  3. Merge any Roboflow datasets (already in YOLO format)
  4. 70 / 30 train / val split (stratified across sources)
  5. Write dataset.yaml for training

Output layout:
  data/cleanbot/
  ├── images/train/   *.jpg
  ├── images/val/     *.jpg
  ├── labels/train/   *.txt
  └── labels/val/     *.txt

Usage:
  python training/prepare_data.py
  python training/prepare_data.py --val-ratio 0.3 --seed 42
"""
import argparse
import json
import random
import shutil
from pathlib import Path

import yaml

DATA_ROOT  = Path(__file__).resolve().parents[3] / "data"
RAW_ROOT   = DATA_ROOT / "raw"
OUT_ROOT   = DATA_ROOT / "cleanbot"
YAML_PATH  = Path(__file__).resolve().parents[1] / "data" / "dataset.yaml"

# ── CleanBot class definitions ────────────────────────────────────────────────
CLASSES = ["plastic", "metal", "paper", "bio_waste"]

# TACO category name → CleanBot class index (-1 = skip)
TACO_MAP: dict[str, int] = {
    # plastic (0)
    "plastic bottle":              0,
    "bottle":                      0,
    "clear plastic bottle":        0,
    "other plastic bottle":        0,
    "plastic bag":                 0,
    "plastic bag & wrapper":       0,
    "plastic film":                0,
    "plastic container":           0,
    "plastic cup":                 0,
    "clear plastic cup":           0,
    "other plastic cup":           0,
    "plastic gloves":              0,
    "plastic utensils":            0,
    "straw":                       0,
    "styrofoam piece":             0,
    "squeezable tube":             0,
    "plastic lid":                 0,
    "lid":                         0,
    "six pack rings":              0,
    "spread tub":                  0,
    "tupperware":                  0,
    "disposable food container":   0,
    "plastic straw":               0,
    # metal (1)
    "aluminium foil":              1,
    "metal bottle cap":            1,
    "bottle cap":                  1,
    "can":                         1,
    "drink can":                   1,
    "food can":                    1,
    "metal can":                   1,
    "pop tab":                     1,
    "scrap metal":                 1,
    "aerosol":                     1,
    "battery":                     1,
    "metal lid":                   1,
    # paper (2)
    "carton":                      2,
    "paper":                       2,
    "paper bag":                   2,
    "paper cup":                   2,
    "newspaper":                   2,
    "magazine paper":              2,
    "cardboard":                   2,
    "toilet tube":                 2,
    "paper straw":                 2,
    # bio_waste (3)
    "food waste":                  3,
    "cigarette":                   3,
    "organic waste":               3,
    # skip
    "broken glass":               -1,
    "glass bottle":               -1,
    "rope & strings":             -1,
    "shoe":                       -1,
    "unlabeled litter":           -1,
    "other litter":               -1,
    "other":                      -1,
    "undefined":                  -1,
}


def coco_to_yolo(bbox: list[float], img_w: int, img_h: int) -> tuple[float, float, float, float]:
    """COCO [x, y, w, h] (top-left pixel) → YOLO [cx, cy, w, h] (normalized)."""
    x, y, w, h = bbox
    cx = (x + w / 2) / img_w
    cy = (y + h / 2) / img_h
    return cx, cy, w / img_w, h / img_h


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def process_taco(records: list[dict]) -> int:
    """
    Parse TACO annotations, convert to YOLO txt files alongside images.
    Returns count of usable annotations.
    """
    taco_data_dir = RAW_ROOT / "taco" / "data"
    anno_path = taco_data_dir / "annotations.json"
    if not anno_path.exists():
        print(f"  TACO annotations not found at {anno_path} — skipping")
        return 0

    with open(anno_path) as f:
        coco = json.load(f)

    # build lookups
    cat_name: dict[int, str] = {c["id"]: c["name"].lower() for c in coco["categories"]}
    img_meta: dict[int, dict] = {img["id"]: img for img in coco["images"]}

    # group annotations by image
    by_image: dict[int, list] = {}
    for ann in coco["annotations"]:
        by_image.setdefault(ann["image_id"], []).append(ann)

    count = 0
    for img_id, anns in by_image.items():
        meta = img_meta.get(img_id)
        if not meta:
            continue

        img_path = taco_data_dir / meta["file_name"]
        if not img_path.exists():
            # TACO file_names often include subdirs like "batch_1/000001.jpg"
            img_path = taco_data_dir / Path(meta["file_name"]).name
        if not img_path.exists():
            continue

        W, H = meta["width"], meta["height"]
        yolo_lines = []
        for ann in anns:
            cname = cat_name.get(ann["category_id"], "")
            cls = TACO_MAP.get(cname, -1)
            if cls == -1:
                continue
            cx, cy, w, h = coco_to_yolo(ann["bbox"], W, H)
            cx, cy, w, h = clamp01(cx), clamp01(cy), clamp01(w), clamp01(h)
            if w < 0.001 or h < 0.001:
                continue
            yolo_lines.append(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        if not yolo_lines:
            continue

        records.append({"image": img_path, "label_lines": yolo_lines, "source": "taco"})
        count += 1

    print(f"  TACO: {count} usable images")
    return count


def process_roboflow_dataset(name: str, records: list[dict]) -> int:
    """
    Roboflow exports already use YOLO format.
    Verify class count matches our 4 classes and collect records.
    """
    base = RAW_ROOT / "roboflow" / name
    if not base.exists():
        print(f"  Roboflow/{name}: not found — skipping")
        return 0

    count = 0
    for split in ["train", "valid", "test"]:
        img_dir = base / split / "images"
        lbl_dir = base / split / "labels"
        if not img_dir.exists():
            continue
        for img_path in img_dir.glob("*.jpg"):
            lbl_path = lbl_dir / img_path.with_suffix(".txt").name
            if not lbl_path.exists():
                continue
            lines = [l.strip() for l in lbl_path.read_text().splitlines() if l.strip()]
            if not lines:
                continue
            records.append({"image": img_path, "label_lines": lines, "source": f"rf_{name}"})
            count += 1

    print(f"  Roboflow/{name}: {count} images")
    return count


def split_and_write(records: list[dict], val_ratio: float, seed: int):
    random.seed(seed)
    random.shuffle(records)

    n_val = int(len(records) * val_ratio)
    val_set   = records[:n_val]
    train_set = records[n_val:]

    for split_name, split_records in [("train", train_set), ("val", val_set)]:
        img_out = OUT_ROOT / "images" / split_name
        lbl_out = OUT_ROOT / "labels" / split_name
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)

        for rec in split_records:
            stem = Path(rec["image"]).stem
            dst_img = img_out / Path(rec["image"]).name
            dst_lbl = lbl_out / f"{stem}.txt"
            shutil.copy2(rec["image"], dst_img)
            dst_lbl.write_text("\n".join(rec["label_lines"]))

    print(f"\nSplit: {len(train_set)} train  /  {len(val_set)} val  "
          f"({100*(1-val_ratio):.0f}/{100*val_ratio:.0f})")


def write_yaml():
    config = {
        "path": str(OUT_ROOT),
        "train": "images/train",
        "val":   "images/val",
        "nc":    4,
        "names": {0: "plastic", 1: "metal", 2: "paper", 3: "bio_waste"},
    }
    YAML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(YAML_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    print(f"dataset.yaml written → {YAML_PATH}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--val-ratio", type=float, default=0.3,
                        help="Fraction of data used for validation (default 0.30)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    records: list[dict] = []

    print("Loading datasets...")
    process_taco(records)
    process_roboflow_dataset("garbage_detection", records)
    process_roboflow_dataset("litter_detection", records)

    if not records:
        print("\nERROR: No images found. Run training/download_data.py first.")
        return

    print(f"\nTotal images collected: {len(records)}")
    split_and_write(records, val_ratio=args.val_ratio, seed=args.seed)
    write_yaml()

    print("\nDataset ready. Next step:")
    print("  python training/train.py")


if __name__ == "__main__":
    main()
