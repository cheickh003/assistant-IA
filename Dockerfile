FROM python:3.11-slim

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && \
    apt-get install -y git ffmpeg pkg-config build-essential \
    libavcodec-dev libavformat-dev libavdevice-dev libavutil-dev \
    libswscale-dev libswresample-dev libavfilter-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
ARG CACHEBUST=1
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Commande de lancement
CMD ["uvicorn", "bot.main:app", "--host", "0.0.0.0", "--port", "8080"] 