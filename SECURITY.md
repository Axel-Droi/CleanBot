# Security & Data Privacy Policy

CleanBot was designed with privacy as a hard constraint from day one. This document describes how data is handled on the robot and what is transmitted off-device.

## What the Robot Sees vs. What It Stores

| Data Type | On-Device Processing | Transmitted Off-Device |
|---|---|---|
| Raw camera frames | Processed and immediately discarded | Never |
| Human faces | Not detected (excluded from training) | Never |
| License plates | Not detected (excluded from training) | Never |
| Waste bounding boxes | Used for pickup decision, then discarded | Never |
| GPS coordinates | Logged locally per pickup event | Yes (coordinate only) |
| Waste category label | Logged locally per pickup event | Yes (category only) |

## On-Device Inference

All vision processing runs on the NVIDIA Jetson Nano. No raw images or video frames are transmitted to any external server. The camera feed is consumed by the YOLOv8 model and then replaced by the next frame — there is no buffer, cache, or recording.

## Telemetry Format

The only data that leaves the robot is a minimal event record:

```json
{
  "timestamp": "2026-01-19T14:32:00Z",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "waste_category": "plastic"
}
```

No images. No video. No personally identifiable information.

## Model Training Scope

The YOLOv8 model was trained exclusively on 4 waste categories: Plastic, Metal, Paper, and Bio-Waste. Human figures, faces, and vehicle identifiers were not included in the training set and are not recognized by the model.

## Reporting a Security Issue

If you discover a vulnerability or a potential privacy concern in this project, please **do not open a public issue**. Instead, email the team directly at the contact provided in the repository. We will respond within 72 hours and coordinate a fix before any public disclosure.

## Scope of Deployment

CleanBot is intended for use in public outdoor spaces. It is not intended for use inside private property, buildings, or any context where privacy expectations differ from a public sidewalk.
