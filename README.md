## Deepfake Detector (Flask + MediaPipe)

This is a simple deepfake video detector with a Flask backend and a modern Bootstrap UI. It uses MediaPipe face mesh and heuristic checks (facial proportions and blurriness) to flag potential deepfakes.

### 1. Requirements

- Python 3.9–3.11
- pip
- On Windows, a working C++ build toolchain may be required for some dependencies.

Install Python from the Microsoft Store or from the official website if you do not have it.

### 2. Local setup on Windows (recommended)

From a PowerShell or Command Prompt window:

```bash
cd C:\Users\arjit\CascadeProjects\deepfake-detector
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
# or
.venv\Scripts\activate.bat   # Command Prompt

pip install --upgrade pip
pip install -r requirements.txt

python app.py
```

Open `http://127.0.0.1:3000` in your browser, upload a small `.mp4/.avi/.mov` video, and click **Analyze Video**.

You can also read `LOCAL_SETUP_WINDOWS.md` for the same steps in more detail.

### 3. Project structure

- `app.py` – Flask application and HTTP endpoints (`/`, `/analyze`, `/history`).
- `templates/index.html` – Main UI (drag-and-drop upload, status, results, and recent history).
- `detector/config.py` – Tunable thresholds and limits for the heuristic detector.
- `detector/video_analysis.py` – Core `analyze_video` function.
- `requirements.txt` – Python dependencies.

### 4. How detection works (heuristic)

The backend:

- Reads frames from the uploaded video using OpenCV.
- Downscales frames for speed.
- Uses MediaPipe Face Mesh to get facial landmarks.
- Computes distances between key points (eyes, nose tip, mouth center) and a ratio to capture facial proportions.
- Measures frame blurriness using the Laplacian variance.
- Flags a frame as “inconsistent” when:
  - Blurriness is below `MIN_BLURRINESS`, or
  - The proportion ratio is outside `[MIN_RATIO, MAX_RATIO]`.
- Samples up to `MAX_FRAMES` frames (skipping by `FRAME_STEP`) and returns:
  - `is_deepfake`: whether the proportion of inconsistent frames exceeds `DEEPFAKE_THRESHOLD`.
  - `confidence`: percentage of inconsistent frames.

All these constants are configured in `detector/config.py`.

### 5. Recent history feature

- Every analysis result is appended to an in-memory list on the server.
- `GET /history` returns the last 20 analyses (filename, timestamp, result, confidence).
- The UI displays these in the **Recent Analyses** section.

Note: history is not persisted across server restarts.

### 6. Deploying with Vercel (recommended architecture)

Because this app does heavy video processing with OpenCV and MediaPipe, it is better to:

- Host the **frontend on Vercel** as a static site.
- Host the **Flask backend** on a Python-friendly service (e.g., Render, Railway, Fly.io, etc.).

#### 6.1. Prepare the frontend for Vercel

1. Copy `templates/index.html` into a separate folder, for example `frontend/index.html`.
2. In that file, change the fetch call from:

```js
fetch('/analyze', { method: 'POST', body: formData })
```

to point to your backend URL, for example:

```js
fetch('https://your-backend.example.com/analyze', {
  method: 'POST',
  body: formData,
});
```

and similarly for `/history`:

```js
fetch('https://your-backend.example.com/history');
```

3. Initialize a small frontend project (or keep it as plain HTML) and push it to a Git repo.

4. On Vercel:
   - Create a new project from that repo.
   - Ensure the build output includes `index.html` at the root (for a pure static site, no build step is needed).

#### 6.2. Deploy the Flask backend

On a Python host like Render/Railway/Fly:

1. Use this repo with `app.py`, `detector/`, and `requirements.txt`.
2. Configure the start command (for example):

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

3. Enable HTTPS via the host (they usually provide it automatically).
4. Set CORS headers (if needed) to allow your Vercel domain.

### 7. Optional: Vercel serverless (advanced)

You can attempt to move the detection logic into a Vercel serverless Python function (e.g., `api/analyze.py`), but:

- Cold starts, memory limits, and execution time limits may cause problems for larger videos.
- The combined size of OpenCV + MediaPipe dependencies is quite large for typical serverless limits.

For a smoother experience, prefer the “Vercel frontend + separate backend” architecture described above.

