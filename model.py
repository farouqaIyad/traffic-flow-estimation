from supervision import ByteTrack,Detections
from ultralytics import YOLO
import numpy as np 


class Model:
    def __init__(self,source_weights_path,conf,device):
        self.model = YOLO(source_weights_path).to(device=device)
        self.tracker = ByteTrack()
        self.conf = conf
    
    def detect_and_track(self,image) -> np.ndarray:
        result = self.model.predict(image,conf = self.conf)[0]
        detections = Detections.from_ultralytics(result)
        detections = self.tracker.update_with_detections(detections)
        return detections