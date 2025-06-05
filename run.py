#!/usr/bin/env python3

import logging
import asyncio
import uvicorn
from app.bot.bot import bot, dp
from app.config import WEBHOOK_URL
from app.main import app
from app.database.models import init_db

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def start_polling():
    # Initialisation de la base de données
    init_db()
    logger.info("Base de données initialisée")

    # Supprimer tout webhook existant
    await bot.delete_webhook(drop_pending_updates=True)

    # Démarrer le bot en mode polling
    logger.info("Démarrage du bot en mode polling")
    await dp.start_polling(bot)

def start_webhook():
    # Initialisation de la base de données au démarrage via lifespan
    logger.info("Démarrage du bot en mode webhook")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Démarrer le bot Telegram")
    parser.add_argument("--mode", type=str, choices=["polling", "webhook"], 
                        default="webhook" if WEBHOOK_URL else "polling",
                        help="Mode de fonctionnement du bot (polling ou webhook)")

    args = parser.parse_args()

    if args.mode == "polling":
        asyncio.run(start_polling())
    else:
        start_webhook()
