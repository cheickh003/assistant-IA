#!/bin/bash

# Script pour exécuter la migration de la base de données
echo "Exécution de la migration de la base de données..."

# Vérification si Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "Docker n'est pas en cours d'exécution. Démarrage de Docker..."
    sudo systemctl start docker
fi

# Vérification si les conteneurs sont en cours d'exécution
if ! docker-compose ps | grep -q "postgres"; then
    echo "Les conteneurs ne sont pas en cours d'exécution. Démarrage des conteneurs..."
    docker-compose up -d
    echo "Attente du démarrage de la base de données..."
    sleep 10
fi

# Copie du script de migration dans le conteneur bot
echo "Copie du script de migration dans le conteneur..."
docker cp migrate_db.py assistant-ia:/app/

# Exécution du script de migration dans le conteneur
echo "Exécution de la migration..."
docker exec assistant-ia python3 /app/migrate_db.py

echo "Migration terminée." 