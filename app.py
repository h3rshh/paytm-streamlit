import streamlit as st
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
import tempfile
import os

# Page config
st.set_page_config(
    page_title="Paytm Logo Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://13.232.164.205:8000"  # Your EC2 API URL

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #00BAE8;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00BAE8;
    }
    .detection-box {
        border: 2px solid #00BAE8;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    /* Make tab text larger */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-list"] button {
        height: 60px !important;
        padding: 10px 20px !important;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def get_model_info():
    """Get model information"""
    try:
        response = requests.get(f"{API_BASE_URL}/model/info", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def predict_image(image_file, confidence=0.25):
    """Send image to API for prediction"""
    try:
        # Reset file pointer to beginning
        image_file.seek(0)
        
        files = {"file": ("image.jpg", image_file, "image/jpeg")}
        params = {"conf": confidence}
        
        st.write(f"🔍 Sending request to: {API_BASE_URL}/predict/image")
        st.write(f"📊 Confidence threshold: {confidence}")
        
        response = requests.post(
            f"{API_BASE_URL}/predict/image",
            files=files,
            params=params,
            timeout=30
        )
        
        st.write(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            st.write(f"✅ API Response received")
            st.write(f"🔢 Raw response: {result}")
            return result
        else:
            st.error(f"❌ API Error: {response.status_code}")
            st.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ Request failed: {str(e)}")
        import traceback
        st.error(f"Full error: {traceback.format_exc()}")
        return None

def predict_video(video_file, confidence=0.25, sample_every=10):
    """Send video to API for prediction"""
    try:
        files = {"file": video_file}
        params = {"conf": confidence, "sample_every": sample_every}
        response = requests.post(
            f"{API_BASE_URL}/predict/video",
            files=files,
            params=params,
            timeout=120
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def create_video_timeline(frames_data):
    """Create video detection timeline"""
    if not frames_data:
        return None
    
    timeline_data = []
    for frame in frames_data:
        for detection in frame['detections']:
            timeline_data.append({
                'frame': frame['frame'],
                'timestamp': frame['timestamp'],
                'class': detection['cls'],
                'confidence': detection['confidence']
            })
    
    if not timeline_data:
        return None
    
    df = pd.DataFrame(timeline_data)
    fig = px.scatter(
        df,
        x='timestamp',
        y='confidence',
        color='class',
        size='confidence',
        title="Logo Detections Over Time",
        labels={'timestamp': 'Time (seconds)', 'confidence': 'Confidence'},
        color_discrete_map={
            'fully_visible': '#00BAE8',
            'partially_visible': '#FF6B6B'
        }
    )
    return fig

def draw_bboxes_on_image(image, detections):
    """Draw bounding boxes on image"""
    if not detections:
        return image
    
    # Convert PIL image to matplotlib format
    fig, ax = plt.subplots(1, figsize=(10, 8))
    ax.imshow(np.array(image))
    
    # Color map for different classes
    colors = {
        'fully_visible': '#00BAE8',
        'partially_visible': '#FF6B6B'
    }
    
    for detection in detections:
        bbox = detection.get('bbox', [])
        cls = detection.get('cls', 'unknown')
        confidence = detection.get('confidence', 0)
        
        if len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            width = x2 - x1
            height = y2 - y1
            
            # Draw rectangle
            rect = patches.Rectangle(
                (x1, y1), width, height,
                linewidth=3,
                edgecolor=colors.get(cls, '#FFFFFF'),
                facecolor='none'
            )
            ax.add_patch(rect)
            
            # Add label
            label = f"{cls}: {confidence:.3f}"
            ax.text(
                x1, y1 - 10,
                label,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=colors.get(cls, '#FFFFFF'), alpha=0.8),
                fontsize=10,
                color='white',
                weight='bold'
            )
    
    ax.axis('off')
    plt.tight_layout()
    
    # Convert matplotlib figure to PIL Image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    result_image = Image.open(buf)
    plt.close()
    
    return result_image

def create_detection_chart(detections):
    """Create detection confidence chart"""
    if not detections:
        return None
    
    df = pd.DataFrame(detections)
    fig = px.bar(
        df, 
        x='cls', 
        y='confidence',
        color='cls',
        title="Detection Confidence by Class",
        color_discrete_map={
            'fully_visible': '#00BAE8',
            'partially_visible': '#FF6B6B'
        }
    )
    fig.update_layout(showlegend=False)
    return fig
    """Create video detection timeline"""
    if not frames_data:
        return None
    
    timeline_data = []
    for frame in frames_data:
        for detection in frame['detections']:
            timeline_data.append({
                'frame': frame['frame'],
                'timestamp': frame['timestamp'],
                'class': detection['cls'],
                'confidence': detection['confidence']
            })
    
    if not timeline_data:
        return None
    
    df = pd.DataFrame(timeline_data)
    fig = px.scatter(
        df,
        x='timestamp',
        y='confidence',
        color='class',
        size='confidence',
        title="Logo Detections Over Time",
        labels={'timestamp': 'Time (seconds)', 'confidence': 'Confidence'},
        color_discrete_map={
            'fully_visible': '#00BAE8',
            'partially_visible': '#FF6B6B'
        }
    )
    return fig

def create_annotated_video(video_path, detection_results, output_path):
    """Create video with bounding boxes drawn on frames with detections"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Use web-compatible codec - try multiple options
        codecs_to_try = [
            ('mp4v', '.mp4'),  # Most compatible
            ('H264', '.mp4'),  # H.264 if available
            ('XVID', '.avi'),  # Fallback
        ]
        
        out = None
        final_output_path = output_path
        
        for codec, ext in codecs_to_try:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)
                test_path = output_path.replace('.mp4', ext).replace('.avi', ext)
                out = cv2.VideoWriter(test_path, fourcc, fps, (width, height))
                if out.isOpened():
                    final_output_path = test_path
                    break
                else:
                    out.release()
            except:
                continue
        
        if out is None or not out.isOpened():
            st.error("Could not create video writer with any codec")
            return None
        
        # Create detection lookup by frame number
        detection_lookup = {}
        for frame_data in detection_results.get('frames', []):
            detection_lookup[frame_data['frame']] = frame_data['detections']
        
        frame_num = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_num += 1
            
            # Draw detections if they exist for this frame
            if frame_num in detection_lookup:
                detections = detection_lookup[frame_num]
                for detection in detections:
                    bbox = detection.get('bbox', [])
                    if len(bbox) == 4:
                        x1, y1, x2, y2 = [int(coord) for coord in bbox]
                        cls = detection.get('cls', 'unknown')
                        confidence = detection.get('confidence', 0)
                        
                        # Choose color based on class (BGR format for OpenCV)
                        color = (232, 186, 0) if cls == 'fully_visible' else (107, 107, 255)  # Blue/Red in BGR
                        
                        # Draw rectangle with thicker border
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
                        
                        # Draw label background
                        label = f"{cls}: {confidence:.3f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 15), 
                                    (x1 + label_size[0] + 10, y1), color, -1)
                        
                        # Draw label text
                        cv2.putText(frame, label, (x1 + 5, y1 - 8), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            out.write(frame)
        
        cap.release()
        out.release()
        
        # Convert to web-compatible format using ffmpeg if available
        try:
            web_output = final_output_path.replace('.mp4', '_web.mp4').replace('.avi', '_web.mp4')
            import subprocess
            
            # Use more compatible ffmpeg settings
            cmd = [
                'ffmpeg', '-i', final_output_path, 
                '-c:v', 'libx264', '-profile:v', 'baseline', '-level', '3.0',
                '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'fast',
                '-movflags', '+faststart', '-f', 'mp4', web_output, '-y'
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Remove original and return web version
            if os.path.exists(web_output):
                try:
                    os.unlink(final_output_path)
                except:
                    pass
                return web_output
            else:
                return final_output_path
                
        except subprocess.CalledProcessError as e:
            st.warning(f"FFmpeg conversion failed: {e.stderr}")
            return final_output_path
        except FileNotFoundError:
            st.info("FFmpeg not available, using OpenCV output")
            return final_output_path
        except Exception as e:
            st.warning(f"Video conversion error: {e}")
            return final_output_path
        
    except Exception as e:
        st.error(f"Error creating annotated video: {e}")
        return None

# Main App
def main():
    st.markdown('<h1 class="main-header">🔍 Paytm Logo Detector</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Settings")
    
    # API Health Check
    is_healthy, health_data = check_api_health()
    if is_healthy:
        st.sidebar.success("✅ API Connected")
        st.sidebar.json(health_data)
    else:
        st.sidebar.error("❌ API Disconnected")
        st.error("Cannot connect to the API. Please check if the backend is running.")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Info", "🖼️ Image Detection", "🎥 Video Detection"])
    
    # Tab 1: Info
    with tab1:
        st.header("Model Information")
        
        model_info = get_model_info()
        if model_info:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Model", model_info['model'])
                st.metric("Input Size", f"{model_info['input_size']}px")
                st.metric("Parameters", model_info['parameters'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Training Dataset", model_info['trained_on'])
                st.metric("Classes", len(model_info['classes']))
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.subheader("Model Performance Metrics")
            metrics_df = pd.DataFrame(model_info['metrics']).T
            st.dataframe(metrics_df, use_container_width=True)
            
            # Performance chart
            fig = px.bar(
                metrics_df.reset_index(),
                x='index',
                y=['precision', 'recall', 'mAP50'],
                title="Model Performance by Class",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Image Detection
    with tab2:
        st.header("Image Logo Detection")
        
        # Main layout: Left column for images, Right column for results
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("📤 Upload & Settings")
            uploaded_image = st.file_uploader(
                "Upload an image",
                type=['png', 'jpg', 'jpeg'],
                help="Upload an image to detect Paytm logos"
            )
            
            confidence = st.slider(
                "Confidence Threshold",
                min_value=0.05,
                max_value=0.95,
                value=0.25,
                step=0.05,
                help="Lower values detect more objects but may include false positives"
            )
            
            # Show original image
            if uploaded_image:
                st.subheader("📷 Original Image")
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Detection button
                detect_button = st.button("� Detect Logos", type="primary", use_container_width=True)
                
                if detect_button:
                    with st.spinner("Analyzing image..."):
                        # Create a copy of the uploaded file for API call
                        image_bytes = uploaded_image.getvalue()
                        image_copy = BytesIO(image_bytes)
                        image_copy.name = uploaded_image.name
                        
                        result = predict_image(image_copy, confidence)
                    
                    if result:
                        # Show image with bounding boxes
                        detections = result.get('detections', [])
                        if detections:
                            st.subheader("🎯 Detected Logos")
                            bbox_image = draw_bboxes_on_image(image, detections)
                            st.image(bbox_image, caption=f"Detected {len(detections)} logo(s)", use_column_width=True)
                        else:
                            st.info("No logos detected - try lowering confidence threshold")
                        
                        # Store result in session state for right column
                        st.session_state['detection_result'] = result
                    else:
                        st.error("❌ Failed to get prediction from API")
                        if 'detection_result' in st.session_state:
                            del st.session_state['detection_result']
        
        with col_right:
            st.subheader("📊 Detection Results")
            
            # Show results if available
            if 'detection_result' in st.session_state:
                result = st.session_state['detection_result']
                
                # Debug: Show raw result
                with st.expander("� Debug: Raw API Response"):
                    st.json(result)
                
                # Metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Detections", result.get('count', 0))
                with col_b:
                    st.metric("Inference Time", f"{result.get('inference_ms', 0):.1f}ms")
                with col_c:
                    st.metric("Model", result.get('model', 'Unknown'))
                
                # Detections details
                detections = result.get('detections', [])
                if detections:
                    st.subheader("🏷️ Detection Details")
                    for i, detection in enumerate(detections, 1):
                        st.markdown(f'<div class="detection-box">', unsafe_allow_html=True)
                        st.write(f"**Detection {i}:**")
                        st.write(f"- **Class:** {detection.get('cls', 'Unknown')}")
                        st.write(f"- **Confidence:** {detection.get('confidence', 0):.4f}")
                        bbox = detection.get('bbox', [])
                        if bbox:
                            st.write(f"- **Bounding Box:** {[round(x, 1) for x in bbox]}")
                        bbox_norm = detection.get('bbox_norm', [])
                        if bbox_norm:
                            st.write(f"- **Normalized:** {[round(x, 4) for x in bbox_norm]}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Chart
                    chart = create_detection_chart(detections)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                else:
                    st.info("No logos detected in the image.")
                    st.write("� Try lowering the confidence threshold or use a different image.")
            else:
                st.info("👆 Upload an image and click 'Detect Logos' to see results here.")
    
    # Tab 3: Video Detection
    with tab3:
        st.header("Video Logo Detection")
        
        # Upload and settings section
        st.subheader("📤 Upload & Configure")
        col_upload, col_settings = st.columns([2, 1])
        
        with col_upload:
            uploaded_video = st.file_uploader(
                "Choose a video file",
                type=['mp4', 'avi', 'mov'],
                help="Upload a video to detect Paytm logos"
            )
        
        with col_settings:
            col_a, col_b = st.columns(2)
            with col_a:
                video_confidence = st.slider(
                    "Confidence Threshold",
                    min_value=0.05,
                    max_value=0.95,
                    value=0.25,
                    step=0.05,
                    key="video_conf"
                )
            
            with col_b:
                sample_every = st.slider(
                    "Sample Every N Frames",
                    min_value=1,
                    max_value=30,
                    value=10,
                    help="Higher values = faster processing, lower values = more thorough analysis"
                )
            
            if uploaded_video:
                analyze_button = st.button("🎥 Analyze Video", type="primary", use_container_width=True)
        
        # Video comparison section (side by side)
        if uploaded_video:
            # Always show original video
            st.subheader("🎬 Video Comparison")
            vid_col1, vid_col2 = st.columns([1.2, 1.2])  # Increased size
            
            with vid_col1:
                st.markdown("**📹 Original Video**")
                st.video(uploaded_video)
            
            with vid_col2:
                if 'video_result' in st.session_state and st.session_state['video_result']:
                    result = st.session_state['video_result']
                    
                    # Check if annotated video exists
                    if 'annotated_video_path' in st.session_state:
                        st.markdown("**🎯 Detected Logos**")
                        try:
                            video_path = st.session_state['annotated_video_path']
                            
                            # Debug info
                            if os.path.exists(video_path):
                                file_size = os.path.getsize(video_path) / (1024*1024)  # MB
                                st.caption(f"📁 Video: {os.path.basename(video_path)} ({file_size:.1f}MB)")
                            
                            with open(video_path, 'rb') as video_file:
                                video_bytes = video_file.read()
                                st.video(video_bytes, format='video/mp4', start_time=0)
                        except Exception as e:
                            st.error(f"Could not display annotated video: {e}")
                            st.info("Video processing completed but display failed. Try a different video format.")
                            
                            # Show debug info
                            if 'annotated_video_path' in st.session_state:
                                debug_path = st.session_state['annotated_video_path']
                                st.code(f"Video path: {debug_path}")
                                st.code(f"File exists: {os.path.exists(debug_path) if debug_path else False}")
                        
                        # Quick stats
                        total_detections = sum(len(frame['detections']) for frame in result['frames'])
                        st.success(f"✅ Found {total_detections} detections in {result.get('processing_ms', 0):.0f}ms")
                    else:
                        st.markdown("**❌ No Detections**")
                        st.video(uploaded_video)
                        st.info("No logos detected - try lowering confidence threshold")
                else:
                    st.markdown("**🔍 Analysis Results**")
                    st.info("👆 Click 'Analyze Video' to see results here")
                    # Show placeholder
                    st.video(uploaded_video, start_time=0)
            
            # Synchronized playback controls
            if 'video_result' in st.session_state and 'annotated_video_path' in st.session_state:
                st.markdown("---")
                st.subheader("🎬 Synchronized Playback Controls")
                
                col_sync1, col_sync2, col_sync3 = st.columns([1, 1, 1])
                
                with col_sync1:
                    if st.button("▶️ Play Both Videos", type="primary", use_container_width=True):
                        st.session_state['sync_play'] = True
                
                with col_sync2:
                    if st.button("⏸️ Pause Both Videos", use_container_width=True):
                        st.session_state['sync_play'] = False
                
                with col_sync3:
                    speed = st.selectbox("Playback Speed", [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0], index=0)
                
                # Create synchronized video players
                if st.session_state.get('sync_play', False):
                    st.markdown("### 🎥 Synchronized Video Comparison")
                    
                    try:
                        # Convert videos to base64 for embedding
                        import base64
                        
                        # Original video
                        original_video_bytes = uploaded_video.getvalue()
                        original_b64 = base64.b64encode(original_video_bytes).decode()
                        
                        # Annotated video
                        annotated_path = st.session_state['annotated_video_path']
                        if os.path.exists(annotated_path):
                            with open(annotated_path, 'rb') as f:
                                annotated_video_bytes = f.read()
                            annotated_b64 = base64.b64encode(annotated_video_bytes).decode()
                            
                            # Determine video format
                            video_format = "video/mp4" if annotated_path.endswith('.mp4') else "video/avi"
                            
                            # HTML with synchronized video players
                            sync_html = f"""
                            <div style="display: flex; gap: 20px; justify-content: center;">
                                <div style="flex: 1; text-align: center;">
                                    <h4>📷 Original Video</h4>
                                    <video id="video1" width="100%" controls preload="metadata">
                                        <source src="data:video/mp4;base64,{original_b64}" type="video/mp4">
                                        Your browser does not support the video tag.
                                    </video>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <h4>🎯 Detected Logos</h4>
                                    <video id="video2" width="100%" controls preload="metadata">
                                        <source src="data:{video_format};base64,{annotated_b64}" type="{video_format}">
                                        Your browser does not support the video tag.
                                    </video>
                                </div>
                            </div>
                            
                            <div style="text-align: center; margin: 20px 0;">
                                <button onclick="playBoth()" style="background: #00BAE8; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">▶️ Play Both</button>
                                <button onclick="pauseBoth()" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">⏸️ Pause Both</button>
                                <button onclick="setSpeed({speed})" style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">🐌 {speed}x Speed</button>
                                <button onclick="syncVideos()" style="background: #ffc107; color: black; border: none; padding: 10px 20px; border-radius: 5px; margin: 5px;">🔄 Sync</button>
                            </div>
                            
                            <script>
                                const video1 = document.getElementById('video1');
                                const video2 = document.getElementById('video2');
                                
                                // Set initial playback speed
                                video1.playbackRate = {speed};
                                video2.playbackRate = {speed};
                                
                                function playBoth() {{
                                    const playPromise1 = video1.play();
                                    const playPromise2 = video2.play();
                                    
                                    // Handle play promises for better browser compatibility
                                    if (playPromise1 !== undefined) {{
                                        playPromise1.catch(error => console.log('Video 1 play error:', error));
                                    }}
                                    if (playPromise2 !== undefined) {{
                                        playPromise2.catch(error => console.log('Video 2 play error:', error));
                                    }}
                                }}
                                
                                function pauseBoth() {{
                                    video1.pause();
                                    video2.pause();
                                }}
                                
                                function setSpeed(speed) {{
                                    video1.playbackRate = speed;
                                    video2.playbackRate = speed;
                                }}
                                
                                function syncVideos() {{
                                    video2.currentTime = video1.currentTime;
                                }}
                                
                                // Auto-sync when video1 seeks
                                video1.addEventListener('seeked', function() {{
                                    video2.currentTime = video1.currentTime;
                                }});
                                
                                // Auto-sync when video1 plays/pauses
                                video1.addEventListener('play', function() {{
                                    setTimeout(() => video2.play(), 50); // Small delay for sync
                                }});
                                
                                video1.addEventListener('pause', function() {{
                                    video2.pause();
                                }});
                                
                                // Error handling
                                video1.addEventListener('error', function(e) {{
                                    console.log('Video 1 error:', e);
                                }});
                                
                                video2.addEventListener('error', function(e) {{
                                    console.log('Video 2 error:', e);
                                }});
                            </script>
                            """
                            
                            st.components.v1.html(sync_html, height=800)  # Increased from 600 to 800
                            
                            st.info("💡 **Tips:** Use the controls above or click on the left video to control both. Videos will auto-sync when you seek or play/pause the original video.")
                        else:
                            st.error(f"Annotated video file not found: {annotated_path}")
                    
                    except Exception as e:
                        st.error(f"Error creating synchronized player: {e}")
                        st.info("Falling back to individual video players above.")
            
            # Process video when button is clicked
            if 'analyze_button' in locals() and analyze_button:
                with st.spinner("🎥 Processing video... This may take a while."):
                    # Save uploaded video to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_video.getvalue())
                        temp_video_path = tmp_file.name
                    
                    # Reset file pointer and send to API
                    uploaded_video.seek(0)
                    result = predict_video(uploaded_video, video_confidence, sample_every)
                
                if result:
                    st.session_state['video_result'] = result
                    
                    # Create annotated video if there are detections
                    total_detections = sum(len(frame['detections']) for frame in result['frames'])
                    if total_detections > 0:
                        with st.spinner("🎨 Creating annotated video..."):
                            annotated_path = temp_video_path.replace('.mp4', '_annotated.mp4')
                            success = create_annotated_video(temp_video_path, result, annotated_path)
                            if success and os.path.exists(success):
                                st.session_state['annotated_video_path'] = success
                            else:
                                st.warning("Could not create annotated video. Showing frame analysis instead.")
                                # Store frames for display instead
                                st.session_state['show_frames'] = True
                    
                    # Clean up original temp file
                    try:
                        os.unlink(temp_video_path)
                    except:
                        pass
                    
                    st.rerun()  # Refresh to show results
                else:
                    st.error("❌ Failed to get prediction from API")
                    if 'video_result' in st.session_state:
                        del st.session_state['video_result']
            
            # Results section below videos
            if 'video_result' in st.session_state and st.session_state['video_result']:
                result = st.session_state['video_result']
                
                st.markdown("---")
                st.subheader("📊 Video Analysis Results")
                
                # Metrics row
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                with metric_col1:
                    st.metric("🎬 Frames Analyzed", result['total_frames_sampled'])
                with metric_col2:
                    st.metric("⚡ Processing Time", f"{result['processing_ms']:.0f}ms")
                with metric_col3:
                    total_detections = sum(len(frame['detections']) for frame in result['frames'])
                    st.metric("🎯 Total Detections", total_detections)
                with metric_col4:
                    frames_with_detections = len([f for f in result['frames'] if f['detections']])
                    st.metric("📈 Detection Rate", f"{frames_with_detections}/{result['total_frames_sampled']}")
                
                # Timeline and details
                detail_col1, detail_col2 = st.columns([1, 1])
                
                with detail_col1:
                    # Timeline chart
                    timeline_chart = create_video_timeline(result['frames'])
                    if timeline_chart:
                        st.subheader("📈 Detection Timeline")
                        st.plotly_chart(timeline_chart, use_container_width=True)
                    else:
                        st.info("No detections found in video frames")
                
                with detail_col2:
                    # Frame-by-frame results
                    st.subheader("🎬 Frame Details")
                    frames_with_detections = [f for f in result['frames'] if f['detections']]
                    
                    if frames_with_detections:
                        # Show summary first
                        st.write(f"**Frames with detections:** {len(frames_with_detections)}")
                        
                        # Expandable frame details
                        for frame in frames_with_detections[:10]:  # Limit to first 10 for performance
                            with st.expander(f"Frame {frame['frame']} (t={frame['timestamp']}s) - {len(frame['detections'])} detections"):
                                for i, detection in enumerate(frame['detections'], 1):
                                    st.write(f"**Detection {i}:**")
                                    st.write(f"- Class: {detection['cls']}")
                                    st.write(f"- Confidence: {detection['confidence']:.4f}")
                                    st.write(f"- BBox: {[round(x, 1) for x in detection['bbox']]}")
                        
                        if len(frames_with_detections) > 10:
                            st.info(f"Showing first 10 frames. Total frames with detections: {len(frames_with_detections)}")
                    else:
                        st.info("No logos detected in any frame.")
                
                # Debug section (collapsible)
                with st.expander("🔍 Debug Information"):
                    st.json(result)

if __name__ == "__main__":
    main()
    print("App running")