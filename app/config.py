import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration du bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN non défini dans les variables d'environnement")

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///chatbot.db")

# Configuration OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration du webhook
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}/{BOT_TOKEN}"
