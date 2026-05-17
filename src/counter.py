# pyrefly: ignore [missing-import]
import cv2
from src.settings_manager import global_settings

class ObjectCounter:
    def __init__(self):
        self.total_count = 0
        self.in_count = 0
        self.out_count = 0

        self.prev_positions = {}
        self.counted_ids = set()

    def reset(self):
        """Reset all counts and track memory. Call before replay or new session."""
        self.total_count = 0
        self.in_count = 0
        self.out_count = 0
        self.prev_positions = {}
        self.counted_ids = set()

    @property
    def line_start(self):
        s = global_settings.get()
        return (s["line_start_x"], s["line_start_y"])

    @property
    def line_end(self):
        s = global_settings.get()
        return (s["line_end_x"], s["line_end_y"])

    def get_side(self, cx, cy):
        return (
            (cx - self.line_start[0])
            * (self.line_end[1] - self.line_start[1])
            -
            (cy - self.line_start[1])
            * (self.line_end[0] - self.line_start[0])
        )

    def update(self, tracks):
        if not tracks:
            return self.total_count
        for track in tracks:
            try:
                # Pastikan track memiliki atribut/index yang benar
                # Ultralytics ByteTrack biasanya mengembalikan: [x1, y1, x2, y2, id, conf, cls]
                if len(track) < 5: continue
                
                x1, y1, x2, y2, track_id = track
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                current_side = self.get_side(cx, cy)

                if track_id not in self.prev_positions:
                    self.prev_positions[track_id] = current_side
                    continue

                previous_side = self.prev_positions[track_id]
                crossed = (
                    previous_side <= 0 and current_side > 0
                ) or (
                    previous_side >= 0 and current_side < 0
                )

                if crossed and track_id not in self.counted_ids:
                    self.total_count += 1
                    self.in_count += 1
                    self.counted_ids.add(track_id)

                self.prev_positions[track_id] = current_side
            except Exception as e:
                print(f"Error updating track: {e}")
                continue
        
        return self.total_count

    def draw(self, frame, tracks, fps=0.0):
        cv2.line(
            frame,
            self.line_start,
            self.line_end,
            (255, 0, 0),
            4
        )
        if tracks:
            for track in tracks:
                if len(track) < 5:
                    continue

                x1, y1, x2, y2, track_id = track

                # bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # center point
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                # label
                cv2.putText(
                    frame,
                    f"ID {track_id}",
                    (x1, y1 - 10),cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
        # metrics
        cv2.putText(
            frame,
            f"IN: {self.in_count}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}", # Menampilkan 1 angka di belakang koma
            (50, 140), # Posisi di bawah Total Coconut
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )
        return frame