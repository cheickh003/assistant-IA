import os
import logging

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
# from aiogram.dispatcher.event.bases import UNHANDLED  # Non requis pour l'instant
from aiogram.exceptions import TelegramBadRequest

from bot.config import BOT_TOKEN, WEB_URL
from bot.agent import agent

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def root_handler(message: types.Message):
    """Redirige le texte utilisateur vers l'agent LangChain."""
    if not message.text:
        await message.answer("Je ne comprends que le texte pour l'instant.")
        return
    answer = agent.invoke(message.text)
    await message.answer(answer)


async def on_startup() -> None:
    """Configure le webhook Telegram."""
    if not WEB_URL:
        logging.warning("WEB_URL n'est pas défini. Le webhook ne sera pas créé.")
        return
    webhook_url = f"{WEB_URL}/webhook/{BOT_TOKEN}"
    try:
        await bot.set_webhook(webhook_url)
        logging.info("Webhook configuré sur %s", webhook_url)
    except TelegramBadRequest as exc:
        logging.error("Erreur de configuration webhook : %s", exc)


app = FastAPI(on_startup=[on_startup])


@app.post(f"/webhook/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """Point d'entrée pour les updates Telegram."""
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "ok"} 