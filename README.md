# CCTV Recorder

This is a Python-based CCTV recording script that captures RTSP streams using `ffmpeg`. It automatically manages storage by deleting old recordings when a size limit is reached and now supports **automatic 10-minute clip splitting**.

## 🎯 Why This Project?
I created this script for my personal use because my IP camera requires a **paid cloud storage service** to store recordings. Since I did not want to pay for it, I searched for free tools but found none that met my needs.  
As a result, I developed this script **with the help of ChatGPT** to provide a **free, local recording solution**.  

If this script is useful to you, feel free to **contribute and improve it!** 🚀  

---

## **🚀 Features**
👉 **Automatic Recording in MP4 Format** (No Corrupt Files)  
👉 **Splits Recordings into 10-Minute Clips** (for easier playback & management)  
👉 **Uses `config.json` for Easy Configuration** (No need to edit Python code)  
👉 **Monitors RTSP Stream & Auto-Reconnects if Disconnected**  
👉 **Prevents Storage Overload** (Deletes old files when disk space exceeds limit)  
👉 **Detailed Logging for Debugging** (`cctv_recorder.log`)  

---

## **🛠 Requirements**
- **Python 3.x**
- **FFmpeg** installed and available in the system path  
  *(For Windows, ensure `ffmpeg.exe` is installed and added to PATH.)*
- **`ffprobe`** for stream checking  

---

## **🗂️ Installation & Setup**
1️⃣ **Install FFmpeg**  
   - **Linux:**  
     ```sh
     sudo apt update && sudo apt install -y ffmpeg
     ```
   - **Windows:**  
     - Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)  
     - Add it to **System PATH**  

2️⃣ **Configure Settings in `config.json`**  
   - Open **`config.json`** and modify the parameters:
     ```json
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
     ```
   - **Key Parameters:**
     - `RTSP_URL` → Your camera's RTSP stream.
     - `OUTPUT_FOLDER` → Location where recordings will be saved.
     - `VIDEO_CLIP_DURATION` → Recording length per file (default: **10 minutes**).
     - `MAX_FOLDER_SIZE_GB` → When exceeded, **oldest recordings are deleted**.

3️⃣ **Run the Script**  
   ```sh
   python cctv_recorder.py
   ```
   👉 The script **will continuously record in 10-minute MP4 files**  
   👉 If the network **disconnects**, it will **auto-restart after reconnection**  

---

## **📆 Storage Management**
- The script **stores recordings in date-based folders** (`YYYY-MM-DD`).
- If the total recording size **exceeds `MAX_FOLDER_SIZE_GB`**, the **oldest files are deleted** automatically.

**Example File Structure:**
```
📂 C:\Users\Godwin\Videos\cctv_entrance\2025-02-23
  ├️ 2025-02-23_10-00-00.mp4  (10 min)
  ├️ 2025-02-23_10-10-00.mp4  (10 min)
  ├️ 2025-02-23_10-20-00.mp4  (10 min)
```

---

## **🛠 Logging & Debugging**
- **All logs are saved in `cctv_recorder.log`** with automatic rotation (5MB per file, max 3 logs).  
- **FFmpeg errors** are saved in `ffmpeg_error.log` (inside the output folder).  

👉 **Check logs if the script stops recording or crashes!**  

---

## **💡 Additional Notes**
- Make sure your **RTSP URL is correct** by testing it in **VLC Media Player** before running the script.
- If you experience **crashes after long network failures**, set up **Task Scheduler** to restart the script automatically.

---

## **📃 License**
This project is open-source and licensed under the **GNU General Public License v3.0 (GPLv3)**.  

**You are free to use, modify, and distribute this script** as long as modifications remain open-source under the same license.  

For more details, see [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html).  

