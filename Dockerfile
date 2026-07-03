FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Fix: Force pip to look into the root directory dependencies directly
RUN pip install fastapi uvicorn pydantic requests

RUN mkdir -p checkpoints/converter

# Moves the model weights safely from their location in your fork
RUN cp converter/checkpoint.pth checkpoints/converter/checkpoint.pth
RUN cp converter/config.json checkpoints/converter/config.json

COPY reference_speaker.wav .
COPY main.py .

# Tell Python to recognize the openvoice folder structure natively
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]
