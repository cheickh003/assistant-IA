import os
import logging
import re

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
# from aiogram.dispatcher.event.bases import UNHANDLED  # Non requis pour l'instant
from aiogram.exceptions import TelegramBadRequest

from bot.config import BOT_TOKEN, WEB_URL
from bot.simple_agent import process_message
from bot.tools import web_search

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def root_handler(message: types.Message):
    """Redirige le texte utilisateur vers l'agent."""
    if not message.text:
        await message.answer("Je ne comprends que le texte pour l'instant.")
        return
    
    user_input = message.text
    
    # Détecte si l'utilisateur demande explicitement une recherche web
    web_search_patterns = [
        r"recherche(?:\s+sur)?(?:\s+internet)?(?:\s+pour)?\s+(.+)",
        r"cherche(?:\s+sur)?(?:\s+internet|web)?\s+(.+)",
        r"trouve(?:\s+sur)?(?:\s+internet|web)?\s+(.+)",
        r"@web\s+(.+)"
    ]
    
    for pattern in web_search_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            await message.answer(f"Je recherche '{query}' sur le web...")
            try:
                results = web_search(query)
                await message.answer(f"Voici les résultats pour '{query}':")
                # Envoie les résultats en plusieurs messages si nécessaire
                for i, result in enumerate(results[:5]):
                    await message.answer(f"{i+1}. {result}")
                return
            except Exception as e:
                await message.answer(f"Désolé, je n'ai pas pu effectuer la recherche : {str(e)}")
                return
    
    # Sinon, traite normalement avec l'agent
    answer = process_message(user_input)
    await message.answer(answer)


# Application FastAPI
app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    """Configure le webhook Telegram."""
    if not WEB_URL:
        logging.warning("WEB_URL n'est pas défini. Le webhook ne sera pas configuré.")
        return
    
    try:
        webhook_url = f"{WEB_URL}/webhook/{BOT_TOKEN}"
        await bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook configuré: {webhook_url}")
    except TelegramBadRequest as e:
        logging.error(f"Erreur lors de la configuration du webhook: {e}")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Supprime le webhook Telegram."""
    await bot.delete_webhook()
    logging.info("Webhook supprimé")


@app.post(f"/webhook/{BOT_TOKEN}")
async def handle_webhook(request: Request):
    """Webhook handler pour Telegram."""
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    """Endpoint de santé."""
    return {"status": "ok"}


# Ajout du mode polling pour les tests locaux
if __name__ == "__main__":
    logging.info("Bot démarré en mode polling")
    import asyncio
    asyncio.run(dp.start_polling(bot)) 