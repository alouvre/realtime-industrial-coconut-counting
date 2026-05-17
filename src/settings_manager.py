import yaml
from pathlib import Path
from src.config import BASE_DIR, CONFIDENCE

TRACKER_YAML_PATH = BASE_DIR / "outputs" / "custom_tracker.yaml"

class SettingsManager:
    def __init__(self):
        # Default Settings (Optimized for high detection recovery (CPU))
        self.settings = {
            "conf_thresh": 0.15,
            "iou_thresh": 0.20,
            "imgsz": 640,
            "track_high_thresh": 0.25,
            "track_low_thresh": 0.10,
            "new_track_thresh": 0.20,
            "match_thresh": 0.75,
            "track_buffer": 90,
            "min_box_area": 20.0,
            "mot20": False,
            "line_start_y": 20,
            "line_end_y": 1260,
            "line_start_x": 560,
            "line_end_x": 590
        }
        self.generate_yaml()

    def update(self, new_settings):
        for k, v in new_settings.items():
            if k in self.settings:
                self.settings[k] = v
        self.generate_yaml()

    def get(self):
        return self.settings

    def generate_yaml(self):
        # Ultralytics ByteTrack config structure
        config = {
            "tracker_type": "bytetrack",
            "track_high_thresh": self.settings["track_high_thresh"],
            "track_low_thresh": self.settings["track_low_thresh"],
            "new_track_thresh": self.settings["new_track_thresh"],
            "track_buffer": int(self.settings["track_buffer"]),
            "match_thresh": self.settings["match_thresh"],
            "min_box_area": int(self.settings["min_box_area"]),
            "mot20": self.settings["mot20"],
            "gmc_method": "sparseOptFlow",
            "proximity_thresh": 0.5,
            "appearance_thresh": 0.25,
            "with_reid": False,
            "fuse_score": True
        }
        
        TRACKER_YAML_PATH.parent.mkdir(exist_ok=True)
        with open(TRACKER_YAML_PATH, "w") as f:
            yaml.dump(config, f)

global_settings = SettingsManager()
