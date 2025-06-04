import cv2

class Camera:
    @staticmethod
    def capture_image():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open webcam")
            
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

