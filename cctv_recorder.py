import os
import time
import subprocess
import logging
import shutil
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Configure rotating log file (5MB per file, keep last 3 logs)
log_handler = RotatingFileHandler(
    "cctv_recorder.log", maxBytes=5 * 1024 * 1024, backupCount=3
)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

# Configuration settings
RTSP_URL = "rtsp url"  # Replace with actual RTSP URL
OUTPUT_FOLDER = "C:\\Users\\Godwin\\Videos\\cctv_entrance"  # Folder to save recordings
MAX_FOLDER_SIZE_GB = 50  # Max allowed storage size in GB
CLIP_DURATION = 180  # Duration of each recording clip in seconds (3 minutes)
CHECK_STREAM_DELAY = 5  # Delay in seconds before checking stream availability after failure
DELETE_CHECK_INTERVAL = 10  # Interval for checking and deleting old files
record_counter = 0  # Counter to track deletion checks

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_folder_size(folder):
    """Calculate folder size in GB."""
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(folder)
        for filename in filenames
    )
    return total_size / (1024 ** 3)

def delete_oldest_files_optimized(folder):
    """Delete oldest files when storage limit is exceeded, checked at intervals."""
    global record_counter
    record_counter += 1
    if record_counter % DELETE_CHECK_INTERVAL != 0:
        return  # Skip deletion check if not at interval
    
    # Get sorted list of files by creation time
    files = sorted(
        (os.path.join(folder, f) for f in os.listdir(folder)),
        key=os.path.getctime
    )
    
    # Delete oldest files until the folder size is within limit
    while get_folder_size(folder) > MAX_FOLDER_SIZE_GB and files:
        oldest = files.pop(0)
        os.remove(oldest)
        logging.info(f"Deleted old file: {oldest}")

def is_rtsp_stream_available():
    """Check if RTSP stream is available using ffprobe."""
    check_command = [
        "ffprobe",
        "-rtsp_transport", "tcp",
        "-i", RTSP_URL,
        "-timeout", "5000000",
        "-show_entries", "format=duration",
        "-v", "quiet"
    ]
    try:
        subprocess.run(check_command, check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def is_vaapi_available():
    """Check if VAAPI (GPU acceleration) is available."""
    return shutil.which("vainfo") is not None

def record_video():
    """Main loop to record RTSP stream, handle failures, and manage storage."""
    while True:
        try:
            # Create folder for today's recordings
            today_folder = os.path.join(OUTPUT_FOLDER, datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(today_folder, exist_ok=True)
            
            # Generate output file name with timestamp
            output_file = os.path.join(today_folder, 
                f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4")
            
            # Check for GPU acceleration support
            if is_vaapi_available():
                logging.info("VAAPI GPU detected. Using hardware acceleration.")
                command = [
                    "ffmpeg",
                    "-hwaccel", "vaapi",
                    "-rtsp_transport", "tcp",
                    "-i", RTSP_URL,
                    "-c:v", "h264_vaapi",  # Use VAAPI encoding
                    "-c:a", "aac", "-b:a", "64k",
                    "-t", str(CLIP_DURATION),
                    "-y",
                    output_file
                ]
            else:
                logging.info("No VAAPI GPU found. Using CPU for recording.")
                command = [
                    "ffmpeg",
                    "-rtsp_transport", "tcp",
                    "-i", RTSP_URL,
                    "-c:v", "copy",  # Copy video stream directly
                    "-c:a", "aac", "-b:a", "64k",
                    "-t", str(CLIP_DURATION),
                    "-y",
                    output_file
                ]

            logging.info(f"Starting recording: {output_file}")
            start_time = time.time()
            
            # Execute FFmpeg command and wait for completion
            process = subprocess.run(command, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=CLIP_DURATION + 30)
            
            logging.info(f"Completed recording in {time.time() - start_time:.1f}s")
            
            # Manage storage by deleting old files if needed
            delete_oldest_files_optimized(OUTPUT_FOLDER)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logging.error(f"Recording failed: {str(e)}")
            
            # Attempt to reconnect if the stream is unavailable
            while True:
                logging.warning("Attempting stream reconnection...")
                if is_rtsp_stream_available():
                    logging.info("Stream reconnected. Resuming recordings.")
                    break
                time.sleep(CHECK_STREAM_DELAY)  # Wait before retrying

if __name__ == "__main__":
    record_video()
