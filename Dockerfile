FROM python:3.10-slim

WORKDIR /app

# Install system audio utilities along with the required C++ compilation tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install packages with a relaxed setup structure to bypass breaking blocks
RUN pip install --no-cache-dir fastapi uvicorn pydantic requests huggingface_hub
RUN pip install --no-cache-dir melotts

COPY reference_speaker.wav .
COPY main.py .

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]
