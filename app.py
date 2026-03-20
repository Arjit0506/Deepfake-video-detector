import os
from flask import Flask, request, render_template, jsonify
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Any
from datetime import datetime

from detector.video_analysis import analyze_video

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

analysis_history: List[Dict[str, Any]] = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400
        
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No video file selected"}), 400
        
    if not video.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        return jsonify({"error": "Invalid file format"}), 400
        
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(video_path)
    
    try:
        result = analyze_video(video_path)
        entry = {
            "filename": video.filename,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "is_deepfake": result.get("is_deepfake"),
            "confidence": result.get("confidence"),
            "message": result.get("message"),
        }
        analysis_history.append(entry)
        os.remove(video_path)  # Clean up uploaded file
        return jsonify(result)
    except Exception as e:
        os.remove(video_path)  # Clean up uploaded file
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    return jsonify(analysis_history[-20:])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)
