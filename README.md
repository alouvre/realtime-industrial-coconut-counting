# Realtime Industrial Coconut Counting System



## Features
|Feature|Detail|
|----|----|
|Coconut detection|YOLOv8n, conf=0.20, iou=0.35, imgsz=416 — optimised for distant coconuts at surveillance resolution|
|Stable track IDs|`_CentroidTracker` with Hungarian assignment `(scipy.optimize.linear_sum_assignment`); EMA velocity smoothing; edge-proximity expiry|
|Smooth motion|Integral velocity decay extrapolation between YOLO updates — boxes decelerate to a stop instead of teleporting|
|Demand-driven CPU||
|Coconut re-ID||
|Behaviour alerts||
|Analytics dashboard||
|NL video search||
|DB persistence||

## Tech Stacks
|Layer|Technology|
|----|----|
|Backend Runtime|Python 3.12, FastAPI, uvicorn (asyncio)|
|ML — detection|YOLOv8n via `ultralytics`|
|ML — re-ID + search|CLIP ViT-B/32 via `open-clip-torch`|
|Coconut tracking|Custom `_CentroidTracker` + `scipy` (Hungarian algorithm)|
|Video decoding|OpenCV (`cv2.VideoCapture`)|
|Message broker|Redis 7 pub/sub|
|Database|PostgreSQL 16 + pgvector extension|
|ORM / migrations||
|Dependency manager|Conda|
|Frontend||
|Containers|Docker Compose — Redis + PostgreSQL only|

## Project Structure

```text
realtime-industrial-coconut-counting/
├── api/                # FastAPI backend server
│   └── server.py
│
├── assets/             #
│   └── video_demo.mp4
├── dashboard/          # Streamlit monitoring dashboard
│   └── app.py
├── models/             # Machine Learning model implementations and artifacts
├── outputs/
├── src/
│   ├── __init__.py
│   ├── config.py            # Global Config (Absolute Paths)
│   ├── counter.py           # Logic Line Crossing & OpenCV Drawing
│   ├── detector.py          # YOLO ByteTrack Wrapper
│   ├── stream_processor.py  # Single Pipeline Manager
│   └── utils.py             # Helper/Utils module
│
├── utils/              # Feature engineering and preprocessing utilities
└── requirements.txt    # Python dependency manifest
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


## License
This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for more information.

## Author
Alifia Mustika Sari - AI/ML Engineer
