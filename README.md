# Paytm Logo Detector - Streamlit Frontend

A beautiful web interface for the Paytm Logo Detection API built with Streamlit.

## Features

### 📊 Info Tab
- Model information and performance metrics
- Training dataset details
- Interactive performance charts

### 🖼️ Image Detection Tab
- Upload images (PNG, JPG, JPEG)
- Adjustable confidence threshold
- Real-time detection results
- Detection confidence visualization
- Bounding box information

### 🎥 Video Detection Tab
- Upload videos (MP4, AVI, MOV)
- Frame sampling control
- Timeline visualization of detections
- Frame-by-frame analysis results

## Setup

### Quick Start
```bash
cd streamlit
chmod +x setup.sh
./setup.sh
```

### Manual Setup with Conda
```bash
cd streamlit
conda create -n streamlit-paytm python=3.11 -y
conda activate streamlit-paytm
pip install -r requirements.txt
```

## Running the App

```bash
# Activate environment
conda activate streamlit-paytm

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Configuration

Update the API URL in `app.py`:
```python
API_BASE_URL = "http://your-api-url:8000"
```

## Dependencies

- streamlit==1.28.1
- requests==2.31.0
- pillow==10.0.1
- pandas==2.1.1
- plotly==5.17.0
- numpy==1.24.3

## API Integration

The app connects to your FastAPI backend and provides:
- Health monitoring
- Image prediction with confidence adjustment
- Video analysis with frame sampling
- Real-time results visualization
- Performance metrics display