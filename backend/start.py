import subprocess
import sys
import time

print("Starting FastAPI backend...")

backend = subprocess.Popen([
    sys.executable,
    "-m",
    "uvicorn",
    "backend.app:app",
    "--host",
    "127.0.0.1",
    "--port",
    "8000"
])

time.sleep(5)

print("Starting Streamlit frontend...")

frontend = subprocess.Popen([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "frontend/streamlit_app.py",
    "--server.address=0.0.0.0",
    "--server.port=3000"
])

frontend.wait()