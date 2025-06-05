import logging
from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from contextlib import asynccontextmanager

from app.config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from app.bot.bot import dp, bot
from app.database.models import init_db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation de la base de données
    init_db()
    logger.info("Base de données initialisée")

    # Configuration du webhook si l'URL est définie
    if WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"Webhook configuré sur {WEBHOOK_URL}")

    yield

    # Nettoyage lors de l'arrêt
    if WEBHOOK_URL:
        await bot.delete_webhook()
        logger.info("Webhook supprimé")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Le service de chatbot Telegram est opérationnel."}

# Configurer le gestionnaire de webhook pour le bot
@app.post(f"{WEBHOOK_PATH}/{BOT_TOKEN}")
async def bot_webhook(request: Request):
    # Traiter les mises à jour du bot
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    return await handler.handle(request)

# Point d'entrée pour exécution directe
if __name__ == "__main__":
    import uvicorn
    logger.info("Démarrage du serveur en mode développement")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
