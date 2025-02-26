CCTV Recorder
This is a Python-based CCTV recording and monitoring system that captures RTSP streams using ffmpeg. It provides a user-friendly GUI, automatic recording, and storage management to ensure continuous video capture without exceeding disk limits.

🎯 Why This Project?
This script was created as a free alternative to paid cloud storage solutions for IP cameras. Many existing tools were either paid, unreliable, or lacked customization. This script provides a local, reliable, and automated recording solution.

👉 Supports both command-line and GUI-based recording!

🚀 Features
✅ Graphical User Interface (GUI) for Control
✅ Automatic Recording at Startup (Optional)
✅ Syncs GUI with Background Script (Detects Running State)
✅ Automatic Recording in MP4 Format (No Corrupt Files)
✅ Splits Recordings into Configurable Time Clips (Default: 10 Minutes)
✅ Auto-Deletes Oldest Files When Storage Limit is Reached
✅ Monitors RTSP Stream & Auto-Reconnects if Disconnected
✅ Prevents Multiple Instances from Running
✅ Detailed JSON-based Logging (cctv_recorder_log.json)
✅ Cross-Platform Support (Windows & Linux)

🖥 GUI Overview
Stopped State
If the script is not running, the GUI shows a stopped status. The Start Recording button is enabled, and the Stop Recording button is disabled.


Settings Window
The Settings window allows configuring the RTSP stream, output folder, storage limit, and video clip duration.


Running State
If the script is running in the background (started manually or at boot), the GUI automatically detects its status and updates accordingly.


🛠 Requirements
1️⃣ Install Python and FFmpeg
Linux
sh
Copy
Edit
sudo apt update && sudo apt install -y ffmpeg python3-opencv python3-pip
Windows
Download & Install FFmpeg from https://ffmpeg.org/download.html
Ensure FFmpeg is added to System PATH
Install Python Dependencies
sh
Copy
Edit
pip install -r requirements.txt
🗂️ Configuration
Modify config.json Before Running
Open config.json and update the settings according to your requirements:

json
Copy
Edit
{
    "RTSP_URL": "rtsp://username:password@camera_ip:554/stream",
    "OUTPUT_FOLDER": "C:\\Users\\Godwin\\Videos\\cctv_entrance",
    "MAX_FOLDER_SIZE_GB": 50,
    "VIDEO_CLIP_DURATION": 600,
    "CHECK_STREAM_DELAY": 5,
    "DELETE_CHECK_INTERVAL": 10,
    "FFMPEG_TIMEOUT": 5000000,
    "AUDIO_BITRATE": "64k"
}
Parameter	Description
RTSP_URL	Camera stream URL
OUTPUT_FOLDER	Folder where recordings are stored
MAX_FOLDER_SIZE_GB	Max storage size before deletion starts
VIDEO_CLIP_DURATION	Duration of each recording file (seconds)
CHECK_STREAM_DELAY	Time between RTSP connection checks
DELETE_CHECK_INTERVAL	How often old recordings are deleted
▶ Running the CCTV Recorder
1️⃣ Run from Command Line
sh
Copy
Edit
python cctv_recorder.py
👉 Starts recording immediately. No GUI.

2️⃣ Run the GUI
sh
Copy
Edit
python cctv_recorder_gui.py
👉 Detects if recording is already running and updates status. Allows manual Start/Stop.

📌 Auto-Start at Boot (Windows & Linux)
Option 1: Auto-Start Recording at Boot (No GUI)
If you want the recording script (cctv_recorder.py) to start automatically without opening the GUI:

Press Win + R and type:
makefile
Copy
Edit
shell:startup
Create a new shortcut with the target:
swift
Copy
Edit
pythonw "C:\path\to\cctv_recorder.py"
The script will start recording automatically when Windows boots.
👉 The GUI can be opened anytime to check the recording status.

Option 2: Auto-Start with GUI (Manual Control)
If you want the GUI (cctv_recorder_gui.py) to open at startup instead:

Press Win + R and type:
makefile
Copy
Edit
shell:startup
Create a new shortcut with the target:
swift
Copy
Edit
pythonw "C:\path\to\cctv_recorder_gui.py"
When the system starts, the GUI will open, allowing you to manually start/stop recording.
👉 If the script is already running in the background, the GUI will detect it and update accordingly.

📆 Storage Management
Recordings are stored in date-based folders (YYYY-MM-DD).
If the total recording size exceeds MAX_FOLDER_SIZE_GB, oldest files are deleted automatically.
Example File Structure:

arduino
Copy
Edit
📂 C:\Users\Godwin\Videos\cctv_entrance\2025-02-23
  ├️ 2025-02-23_10-00-00.mp4  (10 min)
  ├️ 2025-02-23_10-10-00.mp4  (10 min)
  ├️ 2025-02-23_10-20-00.mp4  (10 min)
🛠 Logging & Debugging
All logs are saved in cctv_recorder_log.json with automatic rotation.
FFmpeg errors are captured for debugging.
Example Log Entry:
json
Copy
Edit
{
    "timestamp": "2025-02-23T10:00:00",
    "level": "INFO",
    "message": "Starting new recording: 2025-02-23_10-00-00.mp4"
}
👉 Check logs if the script stops recording or crashes!

💡 Additional Notes
Test your RTSP URL in VLC Player before running the script.
If the script stops unexpectedly, check logs for errors.
Auto-Start Mode: The GUI will not start recording automatically. You must press Start if you want manual control.
Background Mode: If cctv_recorder.py runs at startup, the GUI will fetch its status and allow stopping it if needed.
📃 License
This project is open-source and licensed under the GNU General Public License v3.0 (GPLv3).

For more details, see GPLv3 License.
