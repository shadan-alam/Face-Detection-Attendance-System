import streamlit as st
import time
import psutil
import numpy as np
from datetime import datetime
from collections import deque
from database_operations import DBOperations
from face_recognition import FaceRecognizer
from camera import Camera
import cv2

# Initialize components
face_recognizer = FaceRecognizer()

# Initialize session state
if 'captured_frame' not in st.session_state:
    st.session_state.captured_frame = None
if 'detected_name' not in st.session_state:
    st.session_state.detected_name = None
if 'detected_conf' not in st.session_state:
    st.session_state.detected_conf = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'detection': {
            'total_frames': 0,
            'correct_detections': 0,
            'false_positives': 0,
            'times': deque(maxlen=100)
        },
        'recognition': {
            'correct_predictions': 0,
            'total_predictions': 0,
            'confidences': [],
            'last_5_results': deque(maxlen=5)
        },
        'system': {
            'fps': 0,
            'start_time': time.time(),
            'frame_count': 0,
            'cpu_usage': [],
            'memory_usage': []
        }
    }

def update_system_metrics():
    """Update system performance metrics"""
    st.session_state.metrics['system']['frame_count'] += 1
    elapsed_time = time.time() - st.session_state.metrics['system']['start_time']
    st.session_state.metrics['system']['fps'] = st.session_state.metrics['system']['frame_count'] / elapsed_time
    st.session_state.metrics['system']['cpu_usage'].append(psutil.cpu_percent())
    st.session_state.metrics['system']['memory_usage'].append(psutil.virtual_memory().percent)

def show_metrics_sidebar():
    """Display all metrics in the sidebar"""
    with st.sidebar:
        st.header("📊 Performance Dashboard")
        
        # Detection Metrics
        det_rate = (st.session_state.metrics['detection']['correct_detections'] / 
                   max(1, st.session_state.metrics['detection']['total_frames'])) * 100
        avg_det_time = np.mean(st.session_state.metrics['detection']['times']) * 1000 if st.session_state.metrics['detection']['times'] else 0
        
        st.subheader("🔍 Detection Metrics")
        col1, col2 = st.columns(2)
        col1.metric("Detection Rate", f"{det_rate:.1f}%")
        col2.metric("False Positives", st.session_state.metrics['detection']['false_positives'])
        st.progress(det_rate/100, text=f"Avg Detection: {avg_det_time:.1f}ms")
        
        # Recognition Metrics
        if st.session_state.metrics['recognition']['total_predictions'] > 0:
            accuracy = (st.session_state.metrics['recognition']['correct_predictions'] / 
                      st.session_state.metrics['recognition']['total_predictions']) * 100
            avg_conf = np.mean(st.session_state.metrics['recognition']['confidences']) * 100
            
            st.subheader("👤 Recognition Metrics")
            col1, col2 = st.columns(2)
            col1.metric("Accuracy", f"{accuracy:.1f}%")
            col2.metric("Avg Confidence", f"{avg_conf:.1f}%")
            
            # Confidence distribution
            st.caption("Confidence Distribution")
            conf_bins = np.linspace(0, 1, 5)
            conf_hist, _ = np.histogram(st.session_state.metrics['recognition']['confidences'], bins=conf_bins)
            st.bar_chart(conf_hist)
        
        # System Metrics
        st.subheader("⚙️ System Health")
        col1, col2, col3 = st.columns(3)
        col1.metric("FPS", f"{st.session_state.metrics['system']['fps']:.1f}")
        col2.metric("CPU", f"{np.mean(st.session_state.metrics['system']['cpu_usage']):.1f}%")
        col3.metric("RAM", f"{np.mean(st.session_state.metrics['system']['memory_usage']):.1f}%")
        
        # Performance trends
        st.caption("Performance Trends")
        tab1, tab2 = st.tabs(["CPU", "Memory"])
        with tab1:
            st.line_chart(st.session_state.metrics['system']['cpu_usage'])
        with tab2:
            st.line_chart(st.session_state.metrics['system']['memory_usage'])

# Streamlit UI
st.set_page_config(page_title="Attendoo Analytics", layout="wide")
st.title("🧑✅ Attendoo: Face Attendance System")
show_metrics_sidebar()

st.markdown("---")
st.subheader("📸 Capture & Identify")

# Capture button
if st.button("Capture Photo"):
    with st.spinner("Please Wait.. Accessing Webcam"):
        try:
            start_time = time.time()
            frame = Camera.capture_image()
            
            if frame is not None:
                # RESIZE BEFORE DISPLAY (while keeping aspect ratio)
                scale_percent = 40  # Reduce to 40% of original size
                width = int(frame.shape[1] * scale_percent / 100)
                height = int(frame.shape[0] * scale_percent / 100)
                resized_frame = cv2.resize(frame, (width, height))
                
                # Store original frame for processing, display resized version
                st.session_state.captured_frame = frame  # Keep original for face recognition
                st.image(resized_frame, channels="BGR", caption="Resized Preview", width=200)  # Force display width
                
                # Run face recognition
                name, conf = face_recognizer.predict(frame)
                detection_time = time.time() - start_time
                st.session_state.metrics['detection']['times'].append(detection_time)
                
                st.session_state.detected_name = name
                st.session_state.detected_conf = conf
                st.session_state.metrics['recognition']['confidences'].append(conf)
                st.session_state.metrics['recognition']['last_5_results'].append((name, conf))

                if name:
                    st.session_state.metrics['detection']['correct_detections'] += 1
                    st.session_state.metrics['recognition']['total_predictions'] += 1
                    # For demo, assume correct if confidence > 0.5
                    if conf > 0.5:  
                        st.session_state.metrics['recognition']['correct_predictions'] += 1
                    st.success(f"✅ Recognized as: {name} (Confidence: {conf:.2f})")
                else:
                    st.session_state.metrics['detection']['false_positives'] += 1
                    st.error("❌ No face recognized or confidence too low.")
                
                update_system_metrics()
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
            update_system_metrics()

# Show mark attendance button only if detection was successful
if st.session_state.detected_name:
    # Determine next status
    last_status = DBOperations.get_last_status(st.session_state.detected_name)
    next_status = "Exit" if last_status == "Enter" else "Enter"
    
    # Mark attendance button
    if st.button(f"Mark {next_status} for {st.session_state.detected_name}"):
        success, message = DBOperations.insert_attendance(
            st.session_state.detected_name, 
            next_status
        )
        if success:
            st.success(f"{message} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning(message)

st.markdown("---")
st.caption("Developed by Shadan Alam | 📊 Live Metrics Enabled")