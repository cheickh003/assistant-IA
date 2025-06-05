#!/bin/bash

# Couleurs pour les messages
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}Installation du Chatbot Telegram${NC}"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Vérifier la version de Python
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
echo -e "${YELLOW}Version de Python détectée : ${PYTHON_VERSION}${NC}"

# Créer l'environnement virtuel
echo -e "${YELLOW}Création de l'environnement virtuel...${NC}"
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo -e "${YELLOW}Installation des dépendances...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Configurer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo -e "${YELLOW}Configuration du fichier .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Fichier .env créé. Veuillez le modifier avec vos propres clés API.${NC}"
    echo -e "${YELLOW}Exemple:${NC}"
    echo -e "BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    echo -e "OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz"
fi

# Initialiser la base de données
echo -e "${YELLOW}Initialisation de la base de données...${NC}"
python -c "from app.database.models import init_db; init_db()"

echo -e "${GREEN}Installation terminée !${NC}"
echo -e "${YELLOW}Pour démarrer le bot en mode développement:${NC} python run.py --mode polling"
echo -e "${YELLOW}Pour démarrer le bot en mode production:${NC} python run.py --mode webhook"

# Rendre le script exécutable
chmod +x run.py
