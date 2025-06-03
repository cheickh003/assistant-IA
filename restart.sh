#!/bin/bash

# Script de redémarrage pour l'Assistant IA
echo "Redémarrage de l'Assistant IA..."

# Vérification si Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "Docker n'est pas en cours d'exécution. Démarrage de Docker..."
    sudo systemctl start docker
fi

# Affichage des logs récents pour diagnostic
echo "Logs récents avant redémarrage:"
docker-compose logs --tail=20

# Arrêt des conteneurs
echo "Arrêt des conteneurs..."
docker-compose down

# Suppression des anciens conteneurs arrêtés (optionnel)
echo "Nettoyage des conteneurs arrêtés..."
docker container prune -f

# Redémarrage des conteneurs
echo "Redémarrage des conteneurs..."
docker-compose up -d --build

# Affichage des logs après redémarrage
echo "Logs après redémarrage:"
docker-compose logs --tail=20

echo "Redémarrage terminé! L'API est accessible sur http://localhost:8080"
echo "Pour voir les logs en temps réel: docker-compose logs -f" 