# Daily MKV Processing Service

This project provides a Python-based service designed to monitor a directory for `.mkv` files, process the audio tracks to convert DTS or TrueHD to EAC3 (if necessary), and manage file movement between input and output locations. The script is containerized using Docker for ease of deployment and includes flexible scheduling and runtime configurations.
The purpose is to avoid audio transcoding with Plex remote clients.

---

## Features

- **Audio Track Conversion**: Automatically converts DTS or TrueHD audio tracks in `.mkv` files to EAC3.
- **Daily Scheduling**: Processes files daily at a specified hour.
- **Immediate Run Mode**: Optional mode to skip scheduling constraints and continuously process files.
- **Logging**: Logs are written both to the console and to log files in a dedicated directory.
- **Containerized Deployment**: Easily deployable via Docker.
- **Health Checks**: Ensures the service is running properly within a Docker environment.

---

## Requirements

- **Docker**: Installed on the host system.
- **FFmpeg**: Used for audio conversion (pre-installed in the Docker image).
- **Python 3.9+**: For development outside of Docker.

---

## Setup and Usage

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Build and Run the Docker Container

Modify the `docker-compose.yml` to fit your requirements (see below).

```bash
docker-compose up --build
```

---

### Docker Compose Configuration

#### Example `docker-compose.yml`:

```yaml
services:
  the_boy_savior:
    container_name: the_boy_savior
    build: .
    volumes:
      - ./input:/app/input:rw
      - ./logs:/app/logs:rw
    environment:
      - START_HOUR=11       # Hour to start daily processing
      - RUN_IMMEDIATELY=false # Skip scheduling and continuously process files
    restart: always
    healthcheck:
      test: ["CMD", "pgrep", "-f", "python"]
      interval: 1m
      timeout: 10s
      retries: 3
```

---

### Script Configuration

- **Input Directory**: The script monitors `/app/input` for new `.mkv` files.
- **Logs Directory**: Logs are stored in `/app/logs`.
- **Environment Variables**:
  - `START_HOUR`: The hour (0-23) to start daily processing. Defaults to `11` if not set.
  - `RUN_IMMEDIATELY`: When set to `true`, the script skips the daily schedule and loops every 5 seconds to process files.

---

## Health Checks

The container includes a health check to ensure the Python process is running:

- **Command**: `pgrep -f python`
- **Interval**: Every minute
- **Retries**: 3 consecutive failures mark the container as `unhealthy`.

---

## Development

### Run the Script Locally

Ensure FFmpeg is installed locally and set up the required directories:

1. Install dependencies (if needed):

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export START_HOUR=11
export RUN_IMMEDIATELY=true
```

3. Run the script:

```bash
python script.py
```

---

## Logging

Logs are stored in `/app/logs` and named with the format `YYYY-MM-DD.log`. They include detailed information about:

- File processing start and completion
- Conversion status
- Errors encountered

---

## Troubleshooting

- **Files Not Processing**:
  - Ensure `.mkv` files are present in `/app/input`.
  - Check logs in `/app/logs` for detailed error messages.
- **Health Check Failing**:
  - Ensure the container has sufficient resources.
  - Check the health check configuration in `docker-compose.yml`.

---

## License

This project is licensed under the MIT License.

