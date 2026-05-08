# Realtime Industrial Coconut Counting System



## Features


## Project Structure

```text
/Realtime Industrial Coconut Counting System/
├── api/                # FastAPI backend server
├── dashboard/          # Streamlit monitoring dashboard
├── data/               # Synthetic data generation and storage
├── models/             # Machine Learning model implementations and artifacts
├── utils/              # Feature engineering and preprocessing utilities
├── train.py            # Model training and persistence script
├── main.py             # Project entry point and configuration guide
└── requirements.txt    # Python dependency manifest
```


## System Requirements


## Setup and Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Models**:
   Run the training script to generate the initial synthetic dataset and train the ensemble models.
   ```bash
   python train.py
   ```

3. **Launch Inference API**:
   Start the FastAPI server to handle incoming prediction requests.
   ```bash
   uvicorn api.server:app --reload
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
