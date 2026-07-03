FROM python:3.10-slim

WORKDIR /app

# Install native system audio utilities
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

# Install standard core web frameworks
RUN pip install --no-cache-dir fastapi uvicorn pydantic requests huggingface_hub

# Clean standalone tool downloads that pull the codebase natively into subfolders
RUN git clone https://github.com/myshell-ai/MeloTTS.git melo_src && \
    mv melo_src/melo . && \
    rm -rf melo_src

# Install required numerical libraries for MeloTTS
RUN pip install --no-cache-dir librosa soundfile scipy pydub txt_split nltk

COPY reference_speaker.wav .
COPY main.py .

# Tell Python to recognize the subfolders natively
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]
