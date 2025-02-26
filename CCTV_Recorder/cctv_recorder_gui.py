__version__ = "1.0.0"
import os
import psutil
import tempfile
import subprocess
import time
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

PID_FILE = os.path.join(tempfile.gettempdir(), "cctv_recorder.pid")
SCRIPT_PATH = "cctv_recorder.py"
LOG_FILE = "cctv_recorder_log.json"
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return None

def get_process_status():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        if pid.isdigit() and psutil.pid_exists(int(pid)):
            return True
    return False

def get_latest_recording_filename():
    config = load_config()
    if not config or "OUTPUT_FOLDER" not in config:
        return "No recordings yet"
    
    output_folder = config["OUTPUT_FOLDER"]
    today_folder = os.path.join(output_folder, datetime.now().strftime("%Y-%m-%d"))
    if not os.path.exists(today_folder):
        return "No recordings today"
    
    try:
        mp4_files = sorted(
            (f for f in os.listdir(today_folder) if f.endswith(".mp4")),
            key=lambda f: os.path.getctime(os.path.join(today_folder, f)),
            reverse=True
        )
        return mp4_files[0] if mp4_files else "No recordings yet"
    except Exception:
        return "Error reading folder"

def start_script():
    if get_process_status():
        return
    subprocess.Popen(["python", SCRIPT_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    update_status()

def stop_script():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        if pid.isdigit():
            try:
                process = psutil.Process(int(pid))
                for child in process.children(recursive=True):
                    child.terminate()
                process.terminate()
                process.wait(timeout=5)
                if os.path.exists(PID_FILE):
                    os.remove(PID_FILE)
            except psutil.NoSuchProcess:
                pass
    update_status()

def update_status():
    if get_process_status():
        status_label.configure(text="✅ Running", bootstyle=SUCCESS)
        start_button.configure(state=DISABLED)
        stop_button.configure(state=NORMAL)
    else:
        status_label.configure(text="❌ Stopped", bootstyle=DANGER)
        start_button.configure(state=NORMAL)
        stop_button.configure(state=DISABLED)
    root.after(2000, update_status)

def update_log_display():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()[-10:]
            log_entries = [json.loads(line) for line in lines]
            formatted_logs = "\n".join(f"{entry['timestamp']} [{entry['level']}] {entry['message']}" for entry in reversed(log_entries))
        except Exception as e:
            formatted_logs = f"Error reading log: {e}"
    else:
        formatted_logs = "No logs available."
    
    log_text.config(state=NORMAL)
    log_text.delete(1.0, "end")
    log_text.insert("end", formatted_logs)
    log_text.config(state=DISABLED)
    root.after(2000, update_log_display)

def update_recording_info():
    filename_label.configure(text=f"📁 Current File: {get_latest_recording_filename()}")
    root.after(5000, update_recording_info)

def open_settings():
    """Open the settings window to edit config.json"""
    config_window = ttk.Toplevel(root)
    config_window.title("Settings ⚙️")
    config_window.geometry("1x1")  # Start small to avoid flickering
    config_window.resizable(False, False)

    config_window.update_idletasks()  # Let the window manager process updates

    # Get screen dimensions
    screen_width = config_window.winfo_screenwidth()
    screen_height = config_window.winfo_screenheight()
    window_width = 400
    window_height = 500

    # Calculate x and y position
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Set the final centered position
    config_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Make it modal
    config_window.transient(root)
    config_window.grab_set()

    config = load_config()

    ttk.Label(config_window, text="RTSP URL:").pack(anchor="w", padx=10, pady=5)
    rtsp_entry = ttk.Entry(config_window, width=50)
    rtsp_entry.insert(0, config["RTSP_URL"])
    rtsp_entry.pack(padx=10, pady=5)


    ttk.Label(config_window, text="Output Folder:").pack(anchor="w", padx=10, pady=2)
    output_entry = ttk.Entry(config_window, width=50)
    output_entry.insert(0, config["OUTPUT_FOLDER"])
    output_entry.pack(padx=10, pady=2)

    ttk.Label(config_window, text="Max Folder Size (GB):").pack(anchor="w", padx=10, pady=2)
    max_size_entry = ttk.Entry(config_window, width=50)
    max_size_entry.insert(0, str(config["MAX_FOLDER_SIZE_GB"]))
    max_size_entry.pack(padx=10, pady=2)

    ttk.Label(config_window, text="Video Clip Duration (Seconds):").pack(anchor="w", padx=10, pady=2)
    duration_entry = ttk.Entry(config_window, width=50)
    duration_entry.insert(0, str(config["VIDEO_CLIP_DURATION"]))
    duration_entry.pack(padx=10, pady=2)

    def save_config():
        """Save the updated settings to config.json"""
        config["RTSP_URL"] = rtsp_entry.get()
        config["OUTPUT_FOLDER"] = output_entry.get()
        config["MAX_FOLDER_SIZE_GB"] = int(max_size_entry.get())
        config["VIDEO_CLIP_DURATION"] = int(duration_entry.get())
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
        ttk.Label(config_window, text="✅ Settings Saved!", bootstyle=SUCCESS).pack(pady=5)

    ttk.Button(config_window, text="Save", bootstyle=SUCCESS, command=save_config).pack(pady=10)


root = ttk.Window(themename="darkly")
root.title("CCTV Recorder Control 🎥")
root.geometry("1x1")  # Start with a tiny window to prevent initial flicker
root.resizable(False, False)

root.update_idletasks()  # Let the window manager process the update

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 500
window_height = 450

# Calculate x and y position
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Set the final geometry after update
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill=BOTH)

title_label = ttk.Label(frame, text=f"🎥 CCTV Recorder Control - v{__version__}", font=("Arial", 16, "bold"))
title_label.pack(pady=15)

status_label = ttk.Label(frame, text="⏳ Checking...", font=("Arial", 12, "bold"))
status_label.pack(pady=10)

start_button = ttk.Button(frame, text="▶ Start Recording", bootstyle=SUCCESS, command=start_script)
start_button.pack(pady=10, fill=X, padx=30)

stop_button = ttk.Button(frame, text="⏹ Stop Recording", bootstyle=DANGER, command=stop_script)
stop_button.pack(pady=10, fill=X, padx=30)

settings_button = ttk.Button(frame, text="⚙️ Settings", bootstyle=INFO, command=open_settings)
settings_button.pack(pady=10, fill=X, padx=30)

filename_label = ttk.Label(frame, text="📁 Current File: Loading...", font=("Arial", 10))
filename_label.pack(pady=10)

log_frame = ttk.Labelframe(frame, text="📜 Log Output", padding=10)
log_frame.pack(pady=15, fill=BOTH, expand=True)

log_text = ttk.Text(log_frame, height=8, wrap="word", state=DISABLED)
log_text.pack(fill=BOTH, expand=True)

update_status()
update_recording_info()
update_log_display()

root.mainloop()
