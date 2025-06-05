# Chatbot Telegram avec Mémoire SQLite

Ce projet implémente un chatbot Telegram basique qui peut mémoriser les conversations avec chaque utilisateur dans une base de données SQLite et répondre de manière contextuelle.

## Fonctionnalités

- Interface Telegram pour interagir avec le chatbot
- Mémoire des conversations stockée dans SQLite
- Réponses générées par OpenAI GPT-3.5
- Support du mode polling pour les tests et webhook pour la production
- Déploiement facile avec Docker

## Prérequis

- Python 3.9+
- Token de bot Telegram (via @BotFather)
- Clé API OpenAI

## Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/votre-username/telegram-chatbot.git
cd telegram-chatbot
```

2. Créez et activez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Copiez `.env.example` vers `.env` et configurez vos variables d'environnement :
```bash
cp .env.example .env
# Modifiez .env avec votre éditeur de texte préféré
```

## Configuration

Modifiez le fichier `.env` avec vos propres clés API et paramètres :

```
BOT_TOKEN=votre_token_telegram
OPENAI_API_KEY=votre_cle_openai
DATABASE_URL=sqlite:///chatbot.db
WEBHOOK_HOST=https://votre-domaine.com  # Laisser vide pour le mode polling
WEBHOOK_PATH=/webhook
```

## Utilisation

### Mode développement (polling)

```bash
python run.py --mode polling
```

### Mode production (webhook)

1. Assurez-vous que votre serveur est accessible publiquement avec HTTPS
2. Configurez `WEBHOOK_HOST` dans votre fichier `.env`
3. Lancez l'application :

```bash
python run.py --mode webhook
```

Ou utilisez directement uvicorn :
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Déploiement avec Docker

1. Construisez l'image Docker :
```bash
docker build -t telegram-chatbot .
```

2. Lancez le conteneur :
```bash
docker run -d --name telegram-chatbot -p 8000:8000 --env-file .env telegram-chatbot
```

## Structure du projet

```
.
├── app/                  # Package principal
│   ├── __init__.py
│   ├── config.py        # Configuration de l'application
│   ├── main.py          # Point d'entrée FastAPI
│   ├── bot/             # Module pour le bot Telegram
│   ├── database/        # Modèles et opérations de base de données
│   └── services/        # Services (IA, etc.)
├── .env                 # Variables d'environnement (à créer)
├── .env.example         # Exemple de variables d'environnement
├── Dockerfile           # Configuration Docker
├── README.md            # Documentation
├── requirements.txt     # Dépendances Python
└── run.py               # Script de démarrage
```

## Évolutions futures

Ce projet est une base minimale qui pourra être étendue avec les fonctionnalités suivantes :

- Intégration complète de LangChain pour des agents plus sophistiqués
- Traitement des messages vocaux
- Outils supplémentaires (e-mail, calendrier, recherche web, etc.)
- Gestion multi-utilisateurs avancée
- Interface d'administration web

## Licence

MIT
