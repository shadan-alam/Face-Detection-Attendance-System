# Face-Detection-Attendance-System using InsightFace + YOLO

This project performs face detection and classification on images of 7 different people. It uses **InsightFace** for high-accuracy face localization and **YOLO (You Only Look Once)** for training a lightweight real-time object detector based on the detected faces. A pre trained YOLOv8 model on facial images is trained on the custom dataset created by us for better performance and after training, it is downloaded in my local machine in onnx format..
Link for the pre trained YOLOv8 model--> "https://huggingface.co/arnabdhar/YOLOv8-Face-Detection"
## 📁 Project Structure

```
dataset/
├── images/
│   ├── train/
│   │   ├── 01_0000.jpg
│   │   ├── 01_0001.jpg
│   └── val/
|   └── test/
├── labels/
│   ├── train/
│   │   ├── 01_0000.txt
│   │   ├── 01_0001.txt
│   └── val/
|   └── test/
└── data.yaml  ← defines class names and paths
```
