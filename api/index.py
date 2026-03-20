import os
from flask import Flask, request, jsonify
from detector.video_analysis import analyze_video
import tempfile
import shutil

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Deepfake Video Detector API",
        "endpoints": {
            "analyze": "POST /api/analyze - Upload and analyze video for deepfake detection",
            "health": "GET /api/health - Health check"
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
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
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "Deepfake detector API is running"})

if __name__ == '__main__':
    app.run(debug=True)
