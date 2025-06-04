#!/bin/bash

# Script pour mettre à jour l'assistant IA avec la fonctionnalité de mémorisation
echo "Mise à jour de l'Assistant IA avec la mémorisation..."

# Vérification si Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "Docker n'est pas en cours d'exécution. Démarrage de Docker..."
    sudo systemctl start docker
fi

# Création des nouveaux fichiers
echo "Création des nouveaux fichiers..."
mkdir -p bot

# Mise à jour des fichiers modifiés
echo "Copie des fichiers modifiés sur le serveur..."
# Utilisez votre propre logique de copie ici (scp, git clone, etc.)

# Copie des fichiers dans le conteneur
echo "Copie des fichiers dans le conteneur..."
docker cp bot/memory_agent.py assistant-ia:/app/bot/
docker cp bot/models.py assistant-ia:/app/bot/
docker cp bot/main.py assistant-ia:/app/bot/

# Mise à jour de la base de données pour la nouvelle table UserMemory
echo "Mise à jour de la base de données..."
docker exec assistant-ia python3 -c "from bot.models import create_db_and_tables; create_db_and_tables()"

# Redémarrage du conteneur bot
echo "Redémarrage de l'application..."
docker-compose restart bot

echo "Attente du démarrage complet..."
sleep 5

# Vérification des logs pour confirmer le démarrage
echo "Logs après redémarrage:"
docker-compose logs --tail=20 bot

echo "Mise à jour terminée! Votre bot peut maintenant se souvenir des noms des utilisateurs."
echo "Pour voir les logs en temps réel: docker-compose logs -f bot" 