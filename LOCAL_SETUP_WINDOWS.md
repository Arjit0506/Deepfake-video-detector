## Local Setup on Windows (Python venv)

These are the exact commands to create a virtual environment and run the Flask deepfake detector on Windows (PowerShell or Command Prompt).

### 1. Go to the project folder

```bash
cd C:\Users\arjit\CascadeProjects\deepfake-detector
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

If you have multiple Python versions installed, you may need to use `py` instead:

```bash
py -3 -m venv .venv
```

### 3. Activate the virtual environment

PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Command Prompt:

```bash
.venv\Scripts\activate.bat
```

You should now see `(.venv)` at the beginning of your prompt.

### 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the Flask app

```bash
python app.py
```

By default, the app runs on:

- URL: `http://127.0.0.1:3000`

Open that address in your browser, upload a short video file, and click **Analyze Video**.

### 6. Deactivate the virtual environment (when you are done)

```bash
deactivate
```

