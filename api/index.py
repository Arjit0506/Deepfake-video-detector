import os
from flask import Flask, request, jsonify
import cv2
import numpy as np
import tempfile
import sys

app = Flask(__name__)

# Configure for Railway
port = int(os.environ.get('PORT', 3000))

# Analysis configuration
MIN_BLURRINESS = 100.0
MIN_RATIO = 0.3
MAX_RATIO = 0.7
MAX_FRAMES = 120
FRAME_STEP = 3
DEEPFAKE_THRESHOLD = 50.0

def analyze_video(video_path: str) -> dict:
    """
    Analyze video for potential deepfake indicators using basic video analysis.
    Returns a dict with keys: is_deepfake (bool), confidence (float), message (str).
    """
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    inconsistency_score = 0
    processed_frames = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Downscale frame for faster processing
            height, width = frame.shape[:2]
            scale = 640.0 / max(height, width)
            if scale < 1.0:
                frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

            # Basic analysis without face detection
            blurriness = cv2.Laplacian(frame, cv2.CV_64F).var()
            
            # Check for unusual blurriness or artifacts
            if blurriness < MIN_BLURRINESS:
                inconsistency_score += 1

            # Check frame consistency using edge detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Unusual edge density might indicate artifacts
            if edge_density > 0.1 or edge_density < 0.01:
                inconsistency_score += 1

            processed_frames += 1
            frame_count += 1

            if frame_count % FRAME_STEP != 0:
                continue

            if processed_frames >= MAX_FRAMES:
                break
    finally:
        cap.release()

    if processed_frames == 0:
        return {
            "is_deepfake": False,
            "confidence": 0.0,
            "message": "Could not analyze video - no frames found",
        }

    confidence = (inconsistency_score / processed_frames) * 100.0
    is_deepfake = confidence > DEEPFAKE_THRESHOLD

    return {
        "is_deepfake": is_deepfake,
        "confidence": round(confidence, 2),
        "message": "Video analysis complete (basic mode)",
    }

@app.route('/')
def home():
    return jsonify({
        "message": "Deepfake Video Detector API",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/analyze - Upload and analyze video for deepfake detection",
            "health": "GET /api/health - Health check"
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400
            
        video = request.files['video']
        if video.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
            
        if not video.filename.lower().endswith(('.mp4', '.avi', '.mov')):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            video.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            result = analyze_video(temp_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy", 
        "message": "Deepfake detector API is running",
        "python_version": sys.version
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
