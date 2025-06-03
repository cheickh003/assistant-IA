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

# Installation de psycopg2 si nécessaire
echo "Vérification de la présence de psycopg2 dans le conteneur..."
docker exec assistant-ia pip install psycopg2 2>/dev/null || echo "psycopg2 déjà installé ou impossible à installer"

# Copie des scripts de migration dans le conteneur bot
echo "Copie des scripts de migration dans le conteneur..."
docker cp migrate_db.py assistant-ia:/app/
docker cp migrate_simple.py assistant-ia:/app/

# Exécution du script de migration principal dans le conteneur
echo "Exécution de la migration (version SQLAlchemy)..."
if ! docker exec assistant-ia python3 /app/migrate_db.py; then
    echo "La première méthode a échoué, essai avec la méthode alternative..."
    # Si la première méthode échoue, essayer avec la version simple
    docker exec assistant-ia python3 /app/migrate_simple.py
fi

# Option radicale en cas d'échec des deux méthodes
if [ $? -ne 0 ]; then
    echo "Les deux méthodes ont échoué. Voulez-vous recréer entièrement la base de données? (o/n)"
    read -p "Cette action supprimera toutes les données existantes! " answer
    
    if [ "$answer" = "o" ] || [ "$answer" = "O" ]; then
        echo "Recréation de la base de données..."
        docker-compose down -v
        docker-compose up -d
        echo "Attente du démarrage de la base de données..."
        sleep 10
        echo "Base de données recréée avec succès."
    else
        echo "Opération annulée."
    fi
fi

echo "Migration terminée." 