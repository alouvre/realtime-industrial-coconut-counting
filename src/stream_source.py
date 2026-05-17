"""
StreamSourceManager
===================
Manages the active video/camera source for the detection pipeline.
Supports two modes:
  - "file"   : Local video file playback (plays once, no loop)
  - "live"   : RTSP / IP Camera / USB webcam with auto-reconnect

The manager is a singleton held by the FastAPI process. The frame_generator
in server.py calls get_frame() on every iteration and checks is_finished()
to know when File Playback has ended.
"""

import cv2
import time
import logging
from pathlib import Path
from threading import Lock

logger = logging.getLogger("stream_source")
logging.basicConfig(level=logging.INFO)


class StreamSourceManager:
    MODE_FILE = "file"
    MODE_LIVE = "live"

    def __init__(self):
        self._lock = Lock()
        self._cap: cv2.VideoCapture | None = None

        # Source config (mutable at runtime via /source POST)
        self.mode: str = self.MODE_FILE          # "file" | "live"
        self.file_path: str = ""                 # used in file mode
        self.live_url: str = ""                  # RTSP / webcam index / IP cam URL
        self.reconnect_interval: float = 3.0     # seconds between live reconnect attempts
        self.max_retries: int = 10               # 0 = infinite

        # State
        self.is_finished: bool = False
        self.is_connected: bool = False
        self.is_paused: bool = False
        self.retry_count: int = 0
        self.status_message: str = "Idle"
        self.last_error: str = ""

        # Video metadata (file mode only)
        self.total_frames: int = 0
        self.video_fps: float = 0.0
        self.duration_s: float = 0.0
        self.current_frame: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def configure(self, config: dict):
        """Hot-swap source config. Releases the current cap so the next
        get_frame() call opens the new source."""
        with self._lock:
            self.mode = config.get("mode", self.mode)
            self.file_path = config.get("file_path", self.file_path)
            self.live_url = config.get("live_url", self.live_url)
            self.reconnect_interval = float(config.get("reconnect_interval", self.reconnect_interval))
            self.max_retries = int(config.get("max_retries", self.max_retries))
            self._release_cap()
            self.is_finished = False
            self.is_paused = False
            self.retry_count = 0
            self.current_frame = 0
            self.status_message = "Reconfigured — opening source..."
            logger.info(f"[StreamSource] Reconfigured: mode={self.mode}")

    def replay(self):
        """Restart a finished file from the beginning."""
        with self._lock:
            if self._cap and self._cap.isOpened():
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                self._release_cap()
            self.is_finished = False
            self.is_paused = False
            self.retry_count = 0
            self.current_frame = 0
            self.status_message = "Replaying..."
            logger.info("[StreamSource] Replay requested.")

    def pause(self):
        """Pause stream processing. The capture handle is kept open."""
        with self._lock:
            if not self.is_finished:
                self.is_paused = True
                self.status_message = "Paused"
                logger.info("[StreamSource] Paused.")

    def resume(self):
        """Resume a paused stream."""
        with self._lock:
            self.is_paused = False
            if not self.is_finished:
                self.status_message = "Streaming"
            logger.info("[StreamSource] Resumed.")

    def get_state(self) -> dict:
        elapsed = self.current_frame / self.video_fps if self.video_fps > 0 else 0.0
        remaining = max(0.0, self.duration_s - elapsed)
        progress_pct = round((self.current_frame / self.total_frames * 100) if self.total_frames > 0 else 0.0, 1)
        return {
            "mode": self.mode,
            "file_path": self.file_path,
            "live_url": self.live_url,
            "reconnect_interval": self.reconnect_interval,
            "max_retries": self.max_retries,
            "is_finished": self.is_finished,
            "is_paused": self.is_paused,
            "is_connected": self.is_connected,
            "retry_count": self.retry_count,
            "status_message": self.status_message,
            "last_error": self.last_error,
            # Video metadata
            "total_frames": self.total_frames,
            "video_fps": round(self.video_fps, 2),
            "duration_s": round(self.duration_s, 2),
            "current_frame": self.current_frame,
            "elapsed_s": round(elapsed, 2),
            "remaining_s": round(remaining, 2),
            "progress_pct": progress_pct,
        }

    def read_frame(self):
        """
        Returns (success: bool, frame | None).
        Caller should check is_finished after a failed read in FILE mode.
        Returns (False, None) while paused so the generator can sleep.
        """
        with self._lock:
            # Paused — do not advance the capture
            if self.is_paused:
                return False, None

            # Open source if not already open
            if self._cap is None or not self._cap.isOpened():
                opened = self._open_source()
                if not opened:
                    return False, None

            success, frame = self._cap.read()

            if success:
                self.is_connected = True
                self.retry_count = 0
                self.current_frame += 1
                self.status_message = "Streaming"
                return True, frame

            # ---- Read failed ----
            if self.mode == self.MODE_FILE:
                # File ended — do NOT loop
                self.is_finished = True
                self.is_connected = False
                self.status_message = "Playback Finished"
                logger.info("[StreamSource] File playback finished.")
                return False, None

            # Live mode — reconnect
            self.is_connected = False
            self.retry_count += 1
            self.last_error = "Live stream read failed"
            self.status_message = f"Reconnecting... (attempt {self.retry_count})"
            logger.warning(f"[StreamSource] Live read failed, retry {self.retry_count}")
            self._release_cap()
            return False, None

    def shutdown(self):
        with self._lock:
            self._release_cap()
            self.status_message = "Shutdown"
            logger.info("[StreamSource] Shutdown.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _open_source(self) -> bool:
        if self.mode == self.MODE_FILE:
            if not self.file_path:
                self.status_message = "Error: No file path set"
                self.last_error = "file_path is empty"
                return False
            path = Path(self.file_path)
            if not path.exists():
                self.status_message = f"Error: File not found — {self.file_path}"
                self.last_error = f"File not found: {self.file_path}"
                logger.error(f"[StreamSource] {self.last_error}")
                return False
            self._cap = cv2.VideoCapture(str(path))

        elif self.mode == self.MODE_LIVE:
            src = self.live_url
            # Allow integer webcam index
            if src.isdigit():
                src = int(src)
            self._cap = cv2.VideoCapture(src)

        else:
            self.last_error = f"Unknown mode: {self.mode}"
            return False

        if self._cap and self._cap.isOpened():
            self.is_connected = True
            self.status_message = "Streaming"
            # Extract video metadata (best-effort)
            if self.mode == self.MODE_FILE:
                self.total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.video_fps = self._cap.get(cv2.CAP_PROP_FPS) or 25.0
                self.duration_s = self.total_frames / self.video_fps if self.video_fps > 0 else 0.0
            else:
                self.total_frames = 0
                self.video_fps = 0.0
                self.duration_s = 0.0
            logger.info(f"[StreamSource] Opened source (mode={self.mode}, frames={self.total_frames}, fps={self.video_fps:.1f})")
            return True

        self.last_error = f"cv2.VideoCapture failed to open source"
        self.status_message = f"Error opening source"
        logger.error(f"[StreamSource] {self.last_error}")
        self._cap = None
        return False

    def _release_cap(self):
        if self._cap:
            self._cap.release()
            self._cap = None
        self.is_connected = False
        self.is_paused = False


# Singleton — imported by server.py
global_source_manager = StreamSourceManager()
