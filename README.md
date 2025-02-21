# CCTV Recorder

This is a Python-based CCTV recording script that captures RTSP streams using `ffmpeg`. It automatically manages storage by deleting old recordings when a size limit is reached.

## Why This Project?
I created this script for my personal use because I have an IP camera that requires a paid cloud storage service to store recordings. Since I was not willing to pay for it, I searched extensively for tools but found none that met my needs. As a result, I developed this script with the help of ChatGPT to provide a free, local recording solution. If this script is useful to you, feel free to contribute and improve it!

## Features
- Captures RTSP stream and saves recordings in a structured date-wise folder format.
- Monitors stream availability and attempts reconnection if the stream goes offline.
- Automatically deletes old recordings to maintain storage limits.
- Logs events for monitoring and debugging.

## Requirements
- Python 3.x
- `ffmpeg` installed and available in the system path
- `ffprobe` for stream checking

## Installation
1. Install dependencies (if not already installed):
   ```sh
   sudo apt update && sudo apt install -y ffmpeg
   ```
   *(For Windows, ensure `ffmpeg` is installed and added to PATH.)*
2. Place the script in a directory and configure the `RTSP_URL` and `OUTPUT_FOLDER`.
3. Run the script:
   ```sh
   python cctv_recorder.py
   ```

## Configuration
Edit the following variables in `cctv_recorder.py` to match your setup:
```python
RTSP_URL = "rtsp://username:password@camera_ip:554/stream"
OUTPUT_FOLDER = "C:\\Users\\Godwin\\Videos\\cctv_entrance"
MAX_FOLDER_SIZE_GB = 50
CLIP_DURATION = 180  # Recording duration per file in seconds
```

## Storage Management
- The script ensures the folder size does not exceed `MAX_FOLDER_SIZE_GB` by periodically deleting the oldest recordings.
- Recordings are stored in subfolders named by date (`YYYY-MM-DD`).

## Logging
- Logs are saved in `cctv_recorder.log` with automatic rotation (max 3 logs of 5MB each).
- Errors and reconnection attempts are logged for troubleshooting.

## Notes
- Ensure the `ffmpeg` command works manually before running the script.

## License
This project is open-source and licensed under the **GNU General Public License v3.0 (GPLv3)**. Everyone is free to contribute, modify, and use the script, but any modifications must also be open-sourced under the same license.

For more details, see [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html).
