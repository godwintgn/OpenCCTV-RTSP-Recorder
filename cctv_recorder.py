import os
import time
import json
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ✅ Load Configuration from JSON
CONFIG_FILE = "config.json"

def load_config():
    """Load settings from config.json."""
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

config = load_config()

# ✅ Use settings from config.json
RTSP_URL = config["RTSP_URL"]
OUTPUT_FOLDER = config["OUTPUT_FOLDER"]
MAX_FOLDER_SIZE_GB = config["MAX_FOLDER_SIZE_GB"]
CHECK_STREAM_DELAY = config["CHECK_STREAM_DELAY"]
DELETE_CHECK_INTERVAL = config["DELETE_CHECK_INTERVAL"]
FFMPEG_TIMEOUT = config["FFMPEG_TIMEOUT"]
AUDIO_BITRATE = config["AUDIO_BITRATE"]
VIDEO_CLIP_DURATION = config["VIDEO_CLIP_DURATION"]

# Configure rotating log file (5MB per file, keep last 3 logs)
log_handler = RotatingFileHandler("cctv_recorder.log", maxBytes=5 * 1024 * 1024, backupCount=3)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_folder_size(folder):
    """Calculate total folder size in GB."""
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(folder)
        for filename in filenames
    )
    return total_size / (1024 ** 3)

def delete_oldest_files_optimized(folder):
    """Delete oldest files when storage limit is exceeded."""
    files = sorted(
        (os.path.join(folder, f) for f in os.listdir(folder)),
        key=os.path.getctime
    )

    while get_folder_size(folder) > MAX_FOLDER_SIZE_GB and files:
        oldest = files.pop(0)
        os.remove(oldest)
        logging.info(f"Deleted old file: {oldest}")

def is_rtsp_stream_available():
    """Check if RTSP stream is available using FFmpeg."""
    check_command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", RTSP_URL,
        "-t", "3",  # Try to record 3 seconds
        "-f", "null", "-"  # Discard output, just check connectivity
    ]
    
    try:
        process = subprocess.run(check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return process.returncode == 0  # If return code is 0, stream is OK
    except subprocess.TimeoutExpired:
        return False

def start_recording():
    """Start recording directly in MP4 format."""
    today_folder = os.path.join(OUTPUT_FOLDER, datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(today_folder, exist_ok=True)

    mp4_file = os.path.join(today_folder, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4")

    logging.info(f"Starting new recording: {mp4_file}")

    # log_file = os.path.join(today_folder, "ffmpeg_error.log")  # ✅ Save FFmpeg errors

    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", RTSP_URL,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-movflags", "+frag_keyframe+empty_moov+faststart",  # ✅ Prevents corruption
        "-timeout", str(FFMPEG_TIMEOUT),  # ✅ Load timeout from config.json
        "-t", str(VIDEO_CLIP_DURATION),
        "-y",
        mp4_file
    ]

    with open(log_file, "a") as log:
        process = subprocess.Popen(command, stdout=log, stderr=log)  # ✅ Capture errors

    return process, mp4_file

def monitor_and_recover():
    """Monitor the FFmpeg process, restart if network disconnects."""
    while True:
        process, mp4_file = start_recording()

        while True:
            if process.poll() is not None:  # Check if process has stopped
                logging.warning("FFmpeg stopped unexpectedly. Restarting...")
                break

            time.sleep(1)  # Small delay to reduce CPU usage

            # Check if RTSP stream is down
            if not is_rtsp_stream_available():
                logging.warning("Network disconnected! Stopping current recording...")

                # Kill FFmpeg process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()  # Force kill if needed

                logging.info(f"Recording saved: {mp4_file}")

                # Wait for network to recover
                while not is_rtsp_stream_available():
                    logging.info("Waiting for network reconnection...")
                    time.sleep(CHECK_STREAM_DELAY)

                logging.info("Network reconnected. Starting new recording.")
                break

        delete_oldest_files_optimized(OUTPUT_FOLDER)

if __name__ == "__main__":
    monitor_and_recover()
