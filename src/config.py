from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = str(BASE_DIR / "models" / "best.pt")
VIDEO_PATH = str(BASE_DIR / "assets" / "video_demo.mp4")

CONFIDENCE = 0.25

LINE_START = (560, 20)
LINE_END = (590, 1260)

FRAME_WIDTH = 720
FRAME_HEIGHT = 1280

API_HOST = "0.0.0.0"
API_PORT = 8000