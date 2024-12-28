import os
import shutil
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

INPUT_DIR = "/app/input"
LOG_DIR = "/app/logs"
START_HOUR = int(os.getenv("START_HOUR", 11))  # Default to 11 if not set
RUN_IMMEDIATELY = os.getenv("RUN_IMMEDIATELY", "false").lower() == "true"  # Default to false

log_filename = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

def has_dts_or_truehd(file_path):
    """Check if the file contains DTS or TrueHD audio tracks using ffprobe."""
    command = [
        "ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a",
        "-loglevel", "error", "-print_format", "json"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.warning(f"Failed to analyze audio tracks for {file_path}.")
        return False

    import json
    streams = json.loads(result.stdout).get("streams", [])
    for stream in streams:
        codec_name = stream.get("codec_name", "").lower()
        if codec_name in ["dts", "truehd"]:
            return True
    return False

def convert_audio_tracks(input_file, temp_file):
    """Convert DTS or TrueHD tracks to EAC3."""
    command = [
        "ffmpeg", "-i", input_file, "-hide_banner", "-loglevel", "error", "-b:a", "640k", "-strict", "-2",
        "-fflags", "+genpts", "-map", "0", "-c:v", "copy", "-c:a", "eac3",
        "-c:s", "copy", temp_file, "-y"
    ]
    subprocess.run(command, check=True)

def process_file(file_path):
    filename = os.path.basename(file_path)
    temp_file = os.path.join(os.path.dirname(file_path), f".temp_{filename}")
    new_file_name = os.path.join(os.path.dirname(file_path), filename)

    if has_dts_or_truehd(file_path):
        try:
            logging.info(f"Converting audio tracks for {filename}...")
            convert_audio_tracks(file_path, temp_file)

            logging.info(f"Conversion completed for {filename}.")
            os.remove(file_path)

            logging.info(f"Original file {filename} deleted from input.")
            os.rename(temp_file, new_file_name)
            logging.info(f"File {filename} renamed successfully.")
        except Exception as e:
            logging.error(f"Failed to convert {filename}: {e}")
            return

def main():
    logging.info("Starting watch service...")
    last_run_date = None

    while True:
        now = datetime.now()

        if RUN_IMMEDIATELY:
            logging.info("RUN_IMMEDIATELY is enabled (60s). Skipping daily schedule.")
        elif now.hour >= START_HOUR and (last_run_date is None or last_run_date < now.date()):
            logging.info("Starting daily file processing...")
            last_run_date = now.date()

        if RUN_IMMEDIATELY or last_run_date == now.date():
            for root, _, files in os.walk(INPUT_DIR):
                for file in files:
                    if file.endswith(".mkv"):
                        process_file(os.path.join(root, file))

        time.sleep(60)

if __name__ == "__main__":
    main()
