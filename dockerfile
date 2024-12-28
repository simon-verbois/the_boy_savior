FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir input logs

COPY main.py .

CMD ["python", "-u", "main.py"]
