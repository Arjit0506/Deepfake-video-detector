import os
from flask import Flask, request, jsonify
import tempfile
import sys
import mimetypes

app = Flask(__name__)

# Configure for Railway
port = int(os.environ.get('PORT', 3000))

# Analysis configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
DEEPFAKE_THRESHOLD = 50.0

def analyze_video_basic(video_path: str) -> dict:
    """
    Basic video analysis without OpenCV for serverless environments.
    Analyzes file properties and metadata for potential deepfake indicators.
    """
    try:
        # Get file properties
        file_size = os.path.getsize(video_path)
        
        # Basic file-based analysis
        analysis = {
            "is_deepfake": False,
            "confidence": 0.0,
            "message": "Basic file analysis complete - OpenCV not available in serverless environment",
            "file_info": {
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "analysis_type": "metadata_only"
            },
            "limitations": [
                "OpenCV not available in serverless environment",
                "Video frame analysis requires system libraries",
                "Consider using VPS or container-based deployment for full analysis"
            ]
        }
        
        # Simple heuristic based on file size
        if file_size > MAX_FILE_SIZE:
            analysis["warnings"] = ["Large file size may affect analysis accuracy"]
        
        return analysis
        
    except Exception as e:
        return {
            "is_deepfake": False,
            "confidence": 0.0,
            "message": f"Analysis failed: {str(e)}",
            "error": True
        }

@app.route('/')
def home():
    return jsonify({
        "message": "Deepfake Video Detector API",
        "status": "running",
        "environment": "serverless",
        "capabilities": [
            "File upload and validation",
            "Basic metadata analysis",
            "File size checking"
        ],
        "limitations": [
            "OpenCV not available in serverless environment",
            "No video frame analysis",
            "No deepfake detection capabilities"
        ],
        "endpoints": {
            "analyze": "POST /api/analyze - Upload and analyze video file",
            "health": "GET /api/health - Health check"
        },
        "recommendation": "Deploy on VPS or container-based platform for full functionality"
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400
            
        video = request.files['video']
        if video.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
            
        if not video.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            video.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            result = analyze_video_basic(temp_path)
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
        "environment": "serverless",
        "python_version": sys.version,
        "opencv_available": False,
        "full_analysis": False
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
