# Realtime Industrial Coconut Counting System



## Features


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


## System Requirements
### Techstacks
|Layer|Technology|
|----|----|
|||
|----|----|

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


## Technical Implementation

### Feature Engineering


## License
This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for more information.

## Author
Alifia Mustika Sari - AI/ML Engineer
