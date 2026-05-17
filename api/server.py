import cv2
import asyncio
import time
import logging
from pathlib import Path
from typing import Set

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.stream_processor import StreamProcessor
from src.config import MODEL_PATH, VIDEO_PATH
from src.settings_manager import global_settings
from src.stream_source import global_source_manager

logger = logging.getLogger("server")

app = FastAPI(title="AI Detection API")

# =========================
# INIT COMPONENTS
# =========================
processor = StreamProcessor()

global_source_manager.configure({
    "mode": "file",
    "file_path": VIDEO_PATH,
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════
# CONNECTION MANAGER — multi-client WebSocket hub
# ═══════════════════════════════════════════════

class ConnectionManager:
    """Manages all active WebSocket clients for frame broadcast."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self.active_connections.add(ws)
        logger.info(f"[WS] Client connected. Total: {len(self.active_connections)}")

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self.active_connections.discard(ws)
        logger.info(f"[WS] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast_bytes(self, data: bytes):
        """Send binary frame to all clients. Drop frame for slow clients.
        Snapshots the connection set to avoid mutation during async iteration."""
        async with self._lock:
            targets = list(self.active_connections)
        stale = []
        for ws in targets:
            try:
                await ws.send_bytes(data)
            except Exception:
                stale.append(ws)
        if stale:
            async with self._lock:
                for ws in stale:
                    self.active_connections.discard(ws)

    async def broadcast_text(self, text: str):
        """Send JSON state update to all clients."""
        async with self._lock:
            targets = list(self.active_connections)
        stale = []
        for ws in targets:
            try:
                await ws.send_text(text)
            except Exception:
                stale.append(ws)
        if stale:
            async with self._lock:
                for ws in stale:
                    self.active_connections.discard(ws)

    @property
    def client_count(self) -> int:
        return len(self.active_connections)


ws_manager = ConnectionManager()


# ═══════════════════════════════════════════════
# SHARED FRAME BUFFER — written by inference loop,
#                        read by WebSocket broadcast
# ═══════════════════════════════════════════════

_latest_frame_bytes: bytes = b""
_reset_last_frame: bool = False  # set True by replay to flush stale last_annotated

# ═══════════════════════════════════════════════
# EVENT QUEUE
# ═══════════════════════════════════════════════

action_queue = asyncio.Queue()

def get_current_state_dict():
    src_state = global_source_manager.get_state()
    session = processor.get_session_metrics()
    return {
        # Counting
        "total_count": processor.counter.total_count,
        "in_count": processor.counter.in_count,
        "out_count": processor.counter.out_count,
        "fps": round(processor.fps, 1),
        "status": "active",
        # Stream state
        "stream_status": src_state["status_message"],
        "stream_finished": src_state["is_finished"],
        "stream_paused": src_state["is_paused"],
        "stream_mode": src_state["mode"],
        "ws_clients": ws_manager.client_count,
        # Video progress (file mode)
        "total_frames": src_state["total_frames"],
        "video_fps": src_state["video_fps"],
        "duration_s": src_state["duration_s"],
        "current_frame": src_state["current_frame"],
        "elapsed_s": src_state["elapsed_s"],
        "remaining_s": src_state["remaining_s"],
        "progress_pct": src_state["progress_pct"],
        # Session metrics
        "session_runtime_s": session["session_runtime_s"],
        "processed_frames": session["processed_frames"],
        "replay_count": session["replay_count"],
    }


# ═══════════════════════════════════════════════
# CENTRALIZED INFERENCE LOOP — runs exactly once
# ═══════════════════════════════════════════════

async def inference_loop():
    """
    Single AI pipeline loop. Reads frames from StreamSourceManager,
    runs YOLO + ByteTrack + Counter, encodes JPEG, and broadcasts
    to all WebSocket clients.

    This guarantees one inference pass regardless of client count.
    """
    global _latest_frame_bytes, _reset_last_frame

    last_annotated = None
    LIVE_RECONNECT_SLEEP = 3.0

    while True:
        try:
            # ── Process Async Actions Safely ──
            while not action_queue.empty():
                action = action_queue.get_nowait()
                if action == "replay":
                    processor.reset_session()
                    last_annotated = None
                    _reset_last_frame = False
                    global_source_manager.replay()
                elif action == "toggle_pause":
                    if global_source_manager.is_paused:
                        global_source_manager.resume()
                    else:
                        global_source_manager.pause()
                elif action == "pause":
                    global_source_manager.pause()
                elif action == "resume":
                    global_source_manager.resume()
                elif action == "reset_count":
                    processor.counter.reset()

            # ── Clear stale frame after replay ──
            if _reset_last_frame:
                last_annotated = None
                _reset_last_frame = False

            # ── Finished or Paused: hold last frame ──
            if global_source_manager.is_finished or global_source_manager.is_paused:
                if last_annotated is not None:
                    ret, buffer = cv2.imencode(
                        '.jpg', last_annotated,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                    )
                    if ret:
                        _latest_frame_bytes = buffer.tobytes()
                        await ws_manager.broadcast_bytes(_latest_frame_bytes)
                
                # Broadcast state even while paused
                await ws_manager.broadcast_text(json.dumps(get_current_state_dict()))
                await asyncio.sleep(0.5)
                continue

            # ── Read frame ──
            success, frame = global_source_manager.read_frame()

            if not success:
                if global_source_manager.mode == "live":
                    await asyncio.sleep(LIVE_RECONNECT_SLEEP)
                else:
                    await asyncio.sleep(0.3)
                continue

            # ── AI Pipeline (single pass) ──
            annotated_frame = processor.process_frame(frame)
            last_annotated = annotated_frame

            # ── Encode ──
            ret, buffer = cv2.imencode(
                '.jpg', annotated_frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            )
            if not ret:
                continue

            _latest_frame_bytes = buffer.tobytes()

            # ── Broadcast to all WebSocket clients ──
            await ws_manager.broadcast_bytes(_latest_frame_bytes)
            await ws_manager.broadcast_text(json.dumps(get_current_state_dict()))

            await asyncio.sleep(0.01)

        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"[inference_loop] ERROR: {e}")
            await asyncio.sleep(2)


@app.on_event("startup")
async def startup():
    """Launch the centralized inference loop as a background task."""
    asyncio.create_task(inference_loop())
    logger.info("[Server] Inference loop started.")


# ═══════════════════════════════════════════════
# WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════

@app.websocket("/ws/video")
async def ws_video(ws: WebSocket):
    """
    WebSocket endpoint for realtime video streaming.
    Frames are pushed by the centralized inference loop via ConnectionManager.
    This handler only needs to stay alive and handle client-sent messages
    (heartbeat pings). Uses asyncio.wait_for to avoid blocking on receive.
    """
    await ws_manager.connect(ws)
    try:
        while True:
            try:
                # Wait up to 30s for a client message (ping).
                # Inference loop pushes frames independently via broadcast_bytes.
                msg = await asyncio.wait_for(ws.receive(), timeout=30.0)
                if msg["type"] == "websocket.disconnect":
                    break
                if msg["type"] == "websocket.receive":
                    text = msg.get("text", "")
                    if text == "ping":
                        await ws.send_text("pong")
                    else:
                        try:
                            import json
                            payload = json.loads(text)
                            action = payload.get("action")
                            if action:
                                await action_queue.put(action)
                        except:
                            pass
            except asyncio.TimeoutError:
                # No message from client in 30s — send a keepalive pong
                try:
                    await ws.send_text("keepalive")
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await ws_manager.disconnect(ws)


# ═══════════════════════════════════════════════
# LEGACY MJPEG ENDPOINT (backward compatibility)
# ═══════════════════════════════════════════════

@app.get("/video_feed")
async def video_feed():
    """Legacy MJPEG endpoint — kept for backward compatibility."""
    return StreamingResponse(
        mjpeg_frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


async def mjpeg_frame_generator():
    """Yields frames from the shared buffer for MJPEG clients."""
    while True:
        if _latest_frame_bytes:
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + _latest_frame_bytes + b'\r\n'
            )
        await asyncio.sleep(0.05)


# ═══════════════════════════════════════════════
# REST ENDPOINTS
# ═══════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "status": "OK",
        "message": "AI Counting API is running",
        "endpoints": {
            "health": "/health",
            "settings": "/settings",
            "source": "/source",
            "ws_video": "/ws/video",
            "video_feed": "/video_feed (legacy MJPEG)",
            "stats": "/stats",
        }
    }

@app.get("/health")
async def health():
    src_state = global_source_manager.get_state()
    return {
        "status": src_state["status_message"],
        "stream_connected": src_state["is_connected"],
    }

@app.get("/settings")
async def get_settings():
    return global_settings.get()

@app.post("/settings")
async def update_settings(request: Request):
    new_settings = await request.json()
    global_settings.update(new_settings)
    return {"status": "success", "settings": global_settings.get()}

@app.get("/source")
async def get_source():
    return global_source_manager.get_state()

@app.post("/source")
async def update_source(request: Request):
    config = await request.json()
    global_source_manager.configure(config)
    return {"status": "success", "state": global_source_manager.get_state()}

@app.post("/source/replay")
async def replay_source():
    await action_queue.put("replay")
    return {"status": "queued"}

@app.post("/source/pause")
async def pause_source():
    await action_queue.put("pause")
    return {"status": "queued"}

@app.post("/source/resume")
async def resume_source():
    await action_queue.put("resume")
    return {"status": "queued"}

@app.post("/counter/reset")
async def reset_counter():
    await action_queue.put("reset_count")
    return {"status": "queued"}

@app.get("/stats")
async def get_stats():
    return get_current_state_dict()