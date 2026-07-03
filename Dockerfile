FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Installs the official huggingface downloader tool natively
RUN pip install fastapi uvicorn pydantic requests melotts huggingface_hub

COPY reference_speaker.wav .
COPY main.py .

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]
