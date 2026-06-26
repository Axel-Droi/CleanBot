# CleanBot

**An AI-Powered Autonomous Waste Detection and Community Cleanliness Intelligence Robot**

> Built for the AI Community Challenge — January 2026  
> Team: Shrivats Pandey · Rishabh Mathukiya

---

## The Problem

Urban litter is more than an eyesore. Along creek beds, downtown sidewalks, and near public transit stops, trash accumulates faster than weekly cleanup crews can respond. That gap lets debris spread into storm drains, carrying microplastics into nearby rivers and disproportionately burdening lower-income neighborhoods where cleanup frequency is already lower. Decisions are reactive — made after someone reports a problem, never before one forms.

## The Solution

CleanBot is a closed-loop autonomous robot that predicts, detects, collects, and maps litter in real time. Three cooperative layers work together:

- **Vision layer** — YOLOv8-Nano identifies litter type (plastic, metal, paper, bio-waste) at 30 FPS directly on the robot.
- **Navigation layer** — Q-Learning RL agent optimizes patrol routes using real-time reward signals.
- **Intelligence layer** — A live dashboard maps waste hotspots by neighborhood so city planners can deploy resources proactively.

Unlike passive cameras (which only record) or traditional sweepers (which clean without learning), CleanBot feeds every pickup event back into a spatial database. Patterns emerge. Routes adapt. Resources follow data, not guesses.

---

## Key Features

| Feature | Detail |
|---|---|
| Real-time waste detection | YOLOv8-Nano at ~30 FPS on edge hardware |
| Autonomous navigation | Q-Learning RL with obstacle avoidance via depth camera |
| 4-class waste classification | Plastic · Metal · Paper · Bio-Waste |
| Privacy-first design | No faces, no plates; only GPS coordinates + waste category ever leave the device |
| Live hotspot dashboard | Color-coded neighborhood map updated from robot telemetry |
| Edge-only inference | All vision processing runs locally on NVIDIA Jetson Nano — no cloud round-trips |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CleanBot Robot                       │
│                                                             │
│  Intel RealSense ──► YOLOv8-Nano ──► Waste Classifier      │
│  Depth Camera          (Jetson)       (4 classes)           │
│       │                                    │                │
│       ▼                                    ▼                │
│  Obstacle Map       Q-Learning Agent ◄─ Reward Signal       │
│       │                   │                                 │
│       └──────► Motor      │                                 │
│                Controller │                                 │
│                           ▼                                 │
│              GPS Coord + Waste Category                     │
└───────────────────────┬─────────────────────────────────────┘
                        │  (Stripped telemetry only — no images)
                        ▼
             ┌──────────────────────┐
             │   Community Dashboard │
             │  Hotspot Map · Routes │
             │  Bin Fill Alerts      │
             └──────────────────────┘
```

---

## Hardware Stack

| Component | Specification |
|---|---|
| Compute | NVIDIA Jetson Nano 8GB |
| Vision | Intel RealSense Depth Camera |
| Chassis | 6-Wheel Rocker-Bogie suspension (NASA Mars Rover-inspired) |
| Power | 12V LiPo Battery Bank |

---

## AI & Software Stack

| Layer | Technology |
|---|---|
| Object Detection | YOLOv8-Nano (Ultralytics) |
| Training Framework | PyTorch |
| Edge Optimization | NVIDIA TensorRT |
| Navigation | Q-Learning (custom RL) |
| Dataset | TACO + 500+ custom-labeled local images |

---

## Repository Structure

```
CleanBot/
├── src/
│   ├── vision/          # YOLOv8 inference, data augmentation, training scripts
│   ├── navigation/      # Q-Learning agent, motor controller, obstacle avoidance
│   └── dashboard/       # Hotspot map server and frontend
├── models/              # Trained model weights (tracked via Git LFS)
├── data/                # Dataset manifests (raw images excluded from version control)
├── tests/               # Unit and integration tests
├── docs/                # Technical documentation and diagrams
└── requirements.txt     # Python dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- NVIDIA Jetson Nano with JetPack 4.6+ **or** a CUDA-capable GPU for training
- Intel RealSense SDK 2.0

### Installation

```bash
git clone https://github.com/Axel-Droi/CleanBot.git
cd CleanBot
pip install -r requirements.txt
```

### Running Inference (Jetson Nano)

```bash
python src/vision/detect.py --source /dev/video0 --weights models/cleanbot_nano.pt
```

### Running the RL Navigation Simulation

```bash
python src/navigation/train_agent.py --episodes 1000
```

### Starting the Dashboard

```bash
python src/dashboard/app.py
```

---

## Privacy & Ethics

CleanBot was designed with privacy as a constraint, not an afterthought:

- **No face detection** — the model was trained exclusively on waste categories.
- **No license plate recognition** — deliberately excluded from training data.
- **On-device processing** — raw camera frames are discarded immediately after inference; they never leave the robot.
- **Minimal telemetry** — only GPS coordinates and waste category labels are transmitted.

See [SECURITY.md](SECURITY.md) for the full data handling policy.

---

## Dataset

Training data combines:

- [TACO Dataset](https://github.com/pedropro/TACO) — Trash Annotations in Context (Proença & Simões, 2020)
- 500+ custom-labeled images collected from our local neighborhood

Data augmentation (rotation, flipping, brightness jitter) was applied to improve generalization and eliminate false positives from environmental objects like fallen leaves.

---

## Reward Function (RL Agent)

| Event | Reward |
|---|---|
| Successful trash pickup | +10 |
| Explored new area | +1 |
| Collision with obstacle | -5 |
| Idle time | -1 |

---

## Citations

```
Jocher, G., Chaurasia, A., & Qiu, J. (2023). Ultralytics YOLO (Version 8.0.0).
  https://github.com/ultralytics/ultralytics

Proença, P. F., & Simões, P. (2020). TACO: Trash Annotations in Context for Litter Detection.
  arXiv:2003.06975. https://github.com/pedropro/TACO

Keep America Beautiful. (2021). 2020 National Litter Study.
  https://kab.org/wp-content/uploads/2021/05/2020-National-Litter-Study-Summary-Report.pdf

U.S. Environmental Protection Agency. (2023). Trash Free Waters: Impacts of Mismanaged Trash.
  https://www.epa.gov/trash-free-waters
```

---

## Team

| Name | Role |
|---|---|
| Shrivats Pandey | Vision AI, System Architecture |
| Rishabh Mathukiya | RL Navigation, Hardware Integration |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

AI tools used during development (planning, debugging, documentation):
- **Claude (Anthropic)** — System architecture planning and project outlining
- **ChatGPT (OpenAI)** — Python debugging and data augmentation scripts
- **Gemini (Google)** — Summarizing technical documentation and sensor research
