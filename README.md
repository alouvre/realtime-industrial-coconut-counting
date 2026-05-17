# Realtime Industrial Coconut Counting System

Production-ready realtime coconut detection, tracking, and counting system powered by YOLOv8, FastAPI, and Streamlit. Built for industrial conveyor environments with stable multi-object tracking, realtime analytics, configurable production settings, and low-latency video streaming.

No cloud GPU. No ngrok. No external inference server. Everything runs on an AMD Ryzen 5 5600H.

## Demo

<p align="center">
  <img src="assets/realtime-demo.gif" width="720"/>
</p>

## Features
|Feature|Detail|
|----|----|
|Coconut detection|YOLOv8n with configurable conf, iou, and imgsz parameters optimized for industrial conveyor environments|
|Stable track IDs|ByteTrack + centroid association for stable object IDs during occlusion and overlap|
|Realtime Counting|Line-crossing counting with anti-double-counting logic|
|Live Video Streaming|FastAPI MJPEG/WebSocket stream with realtime overlays|
|Production Dashboard|Streamlit monitoring dashboard with analytics and live controls|
|Dynamic Production Settings|Change detector and tracker configuration directly from dashboard|
|Demand-driven CPU|Optimized inference pipeline to reduce unnecessary CPU usage|
|Error Handling|Automatic reconnect, stream validation, API status monitoring|
|Modular Architecture|Clean architecture for maintainability and scalability|
|Absolute Path Config|Uses pathlib.Path to avoid relative-path runtime issues|
|Industrial Visualization|Bounding box, track ID, center point, FPS, line crossing visualization|


## Tech Stacks
|Layer|Technology|
|----|----|
|Backend Runtime|Python 3.12, FastAPI, uvicorn (asyncio)|
|ML — detection|YOLOv8n via `ultralytics`|
|ML — re-ID + search|CLIP ViT-B/32 via `open-clip-torch`|
|Coconut tracking|Custom `_CentroidTracker` + `scipy` (Hungarian algorithm)|
|Video Decoding|OpenCV (`cv2.VideoCapture`)|
|Message Broker|Redis 7 pub/sub|
|Database|PostgreSQL 16 + pgvector extension|
|ORM / Migrations||
|Environment Manager|Conda|
|Frontend Dashboard|Streamlit|
|Containerization|Docker Compose — Redis + PostgreSQL only|

## Project Structure

```text
realtime-industrial-coconut-counting/
├── api/                # FastAPI backend server
│   └── server.py
│
├── assets/
│   ├── testing_demo.mp4
│   └── realtime_demo.mp4
│
├── dashboard/          # Streamlit monitoring dashboard
│   └── app.py
│
├── models/             # Machine Learning model implementations and artifacts
│
├── outputs/                      # Saved outputs / logs
│
├── src/
│   ├── __init__.py
│   ├── config.py                # Global Configuration (Absolute Paths)
│   ├── counter.py               # Line-crossing Counting Logic
│   ├── detector.py              # YOLOv8 + ByteTrack Wrapper
│   ├── stream_processor.py      # Main realtime pipeline manager
│   ├── source_manager.py        # Source state & playback controller
│   ├── settings_manager.py      # Runtime settings management
│   └── utils.py                 # Utility functions
│
├── requirements.txt
├── README.md
└── LICENSE
```

## Prerequisites
- Python 3.12+ and conda
- Docker + Docker Compose
- Node.js 20+

No GPU, no Google account, no cloud services required.

## Setup and Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Inference API**:
   Start the FastAPI server to handle incoming prediction requests.
   ```bash
   uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
   ```

      Health check:
     ```bash
     curl http://localhost:8000/health
     # {"status":"OK","message":"AI Counting API is running}
     ```

4. **Launch Monitoring Dashboard**:
   Open a separate session to run the visualization layer.
   ```bash
   streamlit run dashboard/app.py
   ```

## API Inference
|Path|Method|Description|
|---|---|---|
|/|GET|Root API endpoint|
|/health|GET|API health status|
|/video_feed|GET|Live MJPEG stream|
|/stats|GET|Realtime counting statistics|
|/source|GET/POST|Source management|
|/source/replay|POST|Replay video source|
|/pause|POST|Pause stream|
|/resume|POST|Resume stream|
/reset_counter|POST|Reset counting statistics|

## License
This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for more information.

## Author
Alifia Mustika Sari - AI/ML Engineer
