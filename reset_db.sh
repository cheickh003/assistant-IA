#!/bin/bash

# Script pour réinitialiser complètement la base de données
echo "ATTENTION: Ce script va supprimer toutes les données existantes et recréer la base de données."
echo "Cette opération est irréversible!"
read -p "Êtes-vous sûr de vouloir continuer? (o/n) " answer

if [ "$answer" != "o" ] && [ "$answer" != "O" ]; then
    echo "Opération annulée."
    exit 1
fi

# Arrêt et suppression des conteneurs et volumes
echo "Arrêt et suppression des conteneurs et volumes..."
docker-compose down -v

# Reconstruction et redémarrage
echo "Reconstruction et redémarrage des conteneurs..."
docker-compose up -d --build

echo "Attente du démarrage complet des services..."
sleep 15

# Vérification que tout fonctionne correctement
echo "Vérification de l'état des conteneurs:"
docker-compose ps

echo "Affichage des logs du conteneur bot:"
docker-compose logs --tail=20 bot

echo "Réinitialisation terminée! La base de données a été entièrement recréée."
echo "Votre bot devrait maintenant fonctionner correctement avec le nouveau schéma de base de données." 