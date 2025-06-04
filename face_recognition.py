from ultralytics import YOLO
from config import MODEL_PATH, MODEL_TASK

class FaceRecognizer:
    def __init__(self):
        self.model = YOLO(MODEL_PATH, task=MODEL_TASK)

    def predict(self, frame):
        try:
            results = self.model.predict(source=frame, save=False, show=False, verbose=False)
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    class_name = r.names[cls_id]
                    conf = float(box.conf[0])
                    return class_name, conf
            return None, None
        except Exception as e:
            raise Exception(f"Prediction error: {e}")