import cv2
import time

from src.detector import YOLODetector
from src.counter import ObjectCounter
from src.config import MODEL_PATH


class StreamProcessor:

    def __init__(self):
        self.detector = YOLODetector(MODEL_PATH)
        self.counter = ObjectCounter()
        self.prev_time = time.time()
        self.fps = 0.0

        # Session metrics
        self.session_start_time: float = time.time()
        self.processed_frames: int = 0
        self.replay_count: int = 0

    def process_frame(self, frame):
        current_time = time.time()
        self.fps = 1.0 / (current_time - self.prev_time + 1e-9)
        self.prev_time = current_time
        self.processed_frames += 1

        tracks = self.detector.detect_and_track(frame)

        self.counter.update(tracks)

        annotated = self.counter.draw(frame, tracks, fps=self.fps)

        return annotated

    def reset_session(self):
        """
        Full monitoring session reset. Call on Replay or new session start.
        Resets:
          - counter (total/in/out/track memory)
          - ByteTrack tracker state (Kalman filters, track IDs)
          - FPS timing (prevents wild first-frame FPS spike)
          - session metrics
        """
        self.counter.reset()
        self.detector.reset_tracker()
        self.prev_time = time.time()   # prevent stale FPS on first post-reset frame
        self.fps = 0.0
        self.processed_frames = 0
        self.session_start_time = time.time()
        self.replay_count += 1

    def get_session_metrics(self) -> dict:
        return {
            "session_start_time": self.session_start_time,
            "session_runtime_s": round(time.time() - self.session_start_time, 1),
            "processed_frames": self.processed_frames,
            "replay_count": self.replay_count,
            "avg_fps": round(self.fps, 1),
        }