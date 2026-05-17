from ultralytics import YOLO
from src.config import MODEL_PATH, CONFIDENCE

from src.settings_manager import global_settings, TRACKER_YAML_PATH

class YOLODetector:
    def __init__(self, model_path=MODEL_PATH):
        self.model = YOLO(model_path)
        print("\n===== MODEL INFO =====")
        self.model.info()
        print("======================\n")

    def reset_tracker(self):
        """
        Flush ByteTrack's internal Kalman filter state between sessions.

        Ultralytics stores tracker state on model.predictor.trackers[0].
        Setting model.predictor = None forces a full rebuild on the next
        model.track() call — new track IDs start from 1, no stale tracks.
        This avoids reloading model weights from disk.
        """
        try:
            if hasattr(self.model, 'predictor') and self.model.predictor is not None:
                if hasattr(self.model.predictor, 'trackers'):
                    self.model.predictor.trackers = []
                self.model.predictor = None
        except Exception as e:
            print(f"[YOLODetector] reset_tracker warning: {e}")

    def detect_and_track(self, frame):
        s = global_settings.get()
        results = self.model.track(
            source=frame,
            persist=True,
            conf=s["conf_thresh"],
            iou=s["iou_thresh"],
            imgsz=s["imgsz"],
            tracker=str(TRACKER_YAML_PATH),
            verbose=False
        )
        tracks = []

        if not results:
            return tracks

        result = results[0]

        if result.boxes is None:
            return tracks

        boxes = result.boxes

        if boxes.id is None:
            return tracks

        for box, track_id in zip(boxes.xyxy.cpu(), boxes.id.cpu()):

            x1, y1, x2, y2 = map(int, box.tolist())

            tracks.append([
                x1,
                y1,
                x2,
                y2,
                int(track_id)
            ])

        return tracks