import asyncio
import os
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from handlers import chat, start

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Configuration du logging pour suivre l'activité du bot
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Point d'entrée principal du bot."""
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if not telegram_token or telegram_token == "METTRE_VOTRE_TOKEN_TELEGRAM_ICI":
        logger.critical("Le TELEGRAM_TOKEN n'est pas défini dans le fichier .env. Le bot ne peut pas démarrer.")
        return

    # Création de l'application PTB
    app = ApplicationBuilder().token(telegram_token).build()

    # Ajout des handlers pour les commandes et les messages
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Lancement du bot en mode polling
    logger.info("Démarrage du bot...")
    await app.run_polling()
    logger.info("Le bot est arrêté.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Arrêt du bot demandé par l'utilisateur (Ctrl+C).")
    except Exception as e:
        logger.critical(f"Une erreur critique a stoppé le bot: {e}") 