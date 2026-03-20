import os
from flask import Flask, request, jsonify
from detector.video_analysis import analyze_video
import tempfile
import sys

app = Flask(__name__)

# Configure for Railway
port = int(os.environ.get('PORT', 3000))

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
