import os
from flask import Flask, request, jsonify
import tempfile
import mimetypes

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
    
    # Basic file analysis without OpenCV
    try:
        # Save file temporarily to get basic info
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            video.save(temp_file.name)
            temp_path = temp_file.name
        
        # Get file size
        file_size = os.path.getsize(temp_path)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(video.filename)
        
        # Basic analysis based on file properties
        analysis = {
            "is_deepfake": False,
            "confidence": 0.0,
            "message": "Basic analysis complete - OpenCV not available on Vercel",
            "file_info": {
                "filename": video.filename,
                "size_bytes": file_size,
                "mime_type": mime_type,
                "size_mb": round(file_size / (1024 * 1024), 2)
            }
        }
        
        # Clean up
        os.unlink(temp_path)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "Deepfake detector API is running"})

if __name__ == '__main__':
    app.run(debug=True)
