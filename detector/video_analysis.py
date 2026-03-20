import cv2
import numpy as np

from . import config


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
            if blurriness < config.MIN_BLURRINESS:
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

            if frame_count % config.FRAME_STEP != 0:
                continue

            if processed_frames >= config.MAX_FRAMES:
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
    is_deepfake = confidence > config.DEEPFAKE_THRESHOLD

    return {
        "is_deepfake": is_deepfake,
        "confidence": round(confidence, 2),
        "message": "Video analysis complete (basic mode)",
    }

