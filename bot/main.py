import os
import logging

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
# from aiogram.dispatcher.event.bases import UNHANDLED  # Non requis pour l'instant
from aiogram.exceptions import TelegramBadRequest

from bot.config import BOT_TOKEN, WEB_URL
from bot.simple_agent import process_message

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def root_handler(message: types.Message):
    """Redirige le texte utilisateur vers l'agent LangChain."""
    if not message.text:
        await message.answer("Je ne comprends que le texte pour l'instant.")
        return
    answer = process_message(message.text)
    await message.answer(answer)


# Application FastAPI
app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    """Configure le webhook Telegram."""
    if not WEB_URL:
        logging.warning("WEB_URL n'est pas défini. Le webhook ne sera pas configuré.")
        return
    
    webhook_url = f"{WEB_URL}/webhook/{BOT_TOKEN}"
    try:
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
async def webhook_endpoint(request: Request):
    """Endpoint pour les mises à jour Telegram."""
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    """Endpoint de santé."""
    return {"status": "ok"}


# Ajout du mode polling pour les tests locaux
if __name__ == "__main__":
    import asyncio
    
    async def main():
        logging.info("Démarrage du bot en mode polling")
        await dp.start_polling(bot)
    
    asyncio.run(main()) 