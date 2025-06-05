FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application
COPY . .

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["python", "run.py", "--mode", "webhook"]
