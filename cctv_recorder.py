import os
import time
import json
import logging
import ffmpeg
import cv2  # ✅ Added OpenCV for RTSP checking
import subprocess
import signal  # ✅ Added signal handling for cleanup
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ✅ Load Configuration from JSON
CONFIG_FILE = "config.json"
PID_FILE = "cctv_recorder.pid"  # ✅ PID file to prevent multiple instances

def load_config():
    """Load settings from config.json."""
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

config = load_config()

# ✅ Use settings from config.json
RTSP_URL              = config["RTSP_URL"]
OUTPUT_FOLDER         = config["OUTPUT_FOLDER"]
MAX_FOLDER_SIZE_GB    = config["MAX_FOLDER_SIZE_GB"]
CHECK_STREAM_DELAY    = config["CHECK_STREAM_DELAY"]
DELETE_CHECK_INTERVAL = config["DELETE_CHECK_INTERVAL"]
FFMPEG_TIMEOUT        = config["FFMPEG_TIMEOUT"]
AUDIO_BITRATE         = config["AUDIO_BITRATE"]
VIDEO_CLIP_DURATION   = config["VIDEO_CLIP_DURATION"]

# ✅ Configure rotating log file in JSON format
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage()
        }
        return json.dumps(log_record)

log_handler = RotatingFileHandler("cctv_recorder_log.json", maxBytes=5 * 1024 * 1024, backupCount=3)
log_handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

# ✅ Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def check_already_running():
    """Prevent multiple script instances using a PID file."""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            old_pid = f.read().strip()
        if old_pid and os.path.exists(f"/proc/{old_pid}"):
            logging.error("Another instance is already running. Exiting...")
            exit(1)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    logging.info("PID file created, script running.")

def cleanup_pid(signum=None, frame=None):
    """Remove the PID file on exit (even if PowerShell is forcefully closed)."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logging.info("PID file removed, script exiting.")
    exit(0)

# ✅ Handle termination signals to ensure cleanup
signal.signal(signal.SIGTERM, cleanup_pid)
signal.signal(signal.SIGINT, cleanup_pid)  # Handles Ctrl+C

def get_folder_size(folder):
    """Calculate total folder size in GB only when necessary."""
    logging.info("Calculating folder size...")
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(folder)
        for filename in filenames
    )
    size_gb = total_size / (1024 ** 3)
    logging.info(f"Folder size: {size_gb:.2f} GB")
    return size_gb

def delete_oldest_files_optimized(folder):
    """Delete oldest MP4 files when storage limit is exceeded and remove empty folders (except today's folder)."""
    logging.info("Checking for files to delete...")
    today_folder = datetime.now().strftime("%Y-%m-%d")
    folder_size = get_folder_size(folder)  # 🔥 Only calculate once
    for root, dirs, files in os.walk(folder, topdown=False):
        mp4_files = sorted(
            (os.path.join(root, f) for f in files if f.endswith(".mp4")),
            key=os.path.getctime
        )
        while folder_size > MAX_FOLDER_SIZE_GB and mp4_files:
            oldest = mp4_files.pop(0)
            os.remove(oldest)
            logging.warning(f"Deleted old file: {oldest}")
            folder_size = get_folder_size(folder)  # 🔥 Update only after deletion
        folder_name = os.path.basename(root)
        if not os.listdir(root) and folder_name != today_folder:
            os.rmdir(root)
            logging.warning(f"Deleted empty folder: {root}")

def is_rtsp_stream_available():
    """Check RTSP stream availability using OpenCV."""
    logging.info("Checking RTSP stream availability...")
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        logging.error("RTSP stream is unavailable.")
        return False
    ret, _ = cap.read()
    cap.release()
    if ret:
        logging.info("RTSP stream is available.")
    else:
        logging.warning("RTSP stream is available but no frames received.")
    return ret

def start_recording():
    """Start recording directly in MP4 format and delete old files if storage is full."""
    logging.info("Starting a new recording...")
    today_folder = os.path.join(OUTPUT_FOLDER, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(today_folder, exist_ok=True)
    delete_oldest_files_optimized(OUTPUT_FOLDER)
    mp4_file = os.path.join(today_folder, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4")
    logging.info(f"Recording to file: {mp4_file}")
    process = (
        ffmpeg.input(RTSP_URL, rtsp_transport='tcp')
        .output(mp4_file, vcodec='copy', acodec='aac', audio_bitrate=AUDIO_BITRATE, 
                movflags='+frag_keyframe+empty_moov+faststart', t=VIDEO_CLIP_DURATION)
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    return process, mp4_file

def monitor_and_recover():
    """Monitor FFmpeg process, restart recording every 10 minutes, and handle network disconnections."""
    logging.info("Starting monitoring loop...")
    try:
        while True:
            process, mp4_file = start_recording()
            start_time = time.time()
            last_rtsp_check = time.time()
            while True:
                if process.poll() is not None:
                    logging.error("FFmpeg process crashed! Restarting recording...")
                    break
                time.sleep(1)
                if time.time() - start_time >= VIDEO_CLIP_DURATION:
                    logging.info("10 minutes completed. Restarting new recording...")
                    process.communicate(b"q")
                    time.sleep(2)
                    break
                if time.time() - last_rtsp_check >= CHECK_STREAM_DELAY:
                    last_rtsp_check = time.time()
                    if not is_rtsp_stream_available():
                        logging.warning("Network disconnected! Stopping current recording...")
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except Exception:
                            process.kill()
                        logging.info(f"Recording saved: {mp4_file}")
                        while not is_rtsp_stream_available():
                            logging.info("Waiting for network reconnection...")
                            time.sleep(10)
                        logging.info("Network reconnected. Starting new recording.")
                        break
    finally:
        cleanup_pid()

if __name__ == "__main__":
    check_already_running()
    logging.info("CCTV Recorder script started.")
    monitor_and_recover()
