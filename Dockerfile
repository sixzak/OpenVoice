FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install -e .
RUN pip install fastapi uvicorn pydantic

RUN mkdir -p checkpoints/converter

# Moves the model weights that are already inside your repository into place
RUN cp converter/checkpoint.pth checkpoints/converter/checkpoint.pth
RUN cp converter/config.json checkpoints/converter/config.json

COPY reference_speaker.wav .
COPY main.py .

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]
