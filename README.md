# Face-Detection-Attendance-System using InsightFace + YOLO

This project performs face detection and classification on images of 7 different people. It uses **InsightFace** for high-accuracy face localization and **YOLO (You Only Look Once)** for training a lightweight real-time object detector based on the detected faces.
## 📁 Project Structure

```
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
└── data.yaml  ← defines class names and paths
```
