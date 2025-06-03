#!/bin/bash

# Script de déploiement pour Assistant IA
echo "Déploiement de l'Assistant IA..."

# Vérification de Docker et Docker Compose
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Installation en cours..."
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "Docker a été installé. Veuillez vous déconnecter et vous reconnecter pour appliquer les changements de groupe."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose n'est pas installé. Installation en cours..."
    sudo apt update
    sudo apt install -y docker-compose-plugin
fi

# Vérification de la présence du fichier d'environnement
if [ ! -f "local.env" ]; then
    echo "Le fichier local.env n'existe pas. Création à partir du modèle..."
    cp env.template local.env
    echo "Veuillez éditer le fichier local.env avec vos propres clés API et tokens."
    exit 1
fi

# Construction et démarrage des conteneurs
echo "Construction et démarrage des conteneurs..."
docker-compose up -d --build

echo "Déploiement terminé! L'API est accessible sur http://localhost:8080"
echo "Pour voir les logs: docker-compose logs -f" 