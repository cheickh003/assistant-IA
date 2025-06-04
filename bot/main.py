import os
import logging
import re

from fastapi import FastAPI, Request, Depends
from aiogram import Bot, Dispatcher, types
# from aiogram.dispatcher.event.bases import UNHANDLED  # Non requis pour l'instant
from aiogram.exceptions import TelegramBadRequest
from sqlmodel import Session, select

from bot.config import BOT_TOKEN, WEB_URL
# Remplacer l'ancien agent par le nouvel agent avec mémoire
from bot.memory_agent import process_message_with_memory
from bot.tools import web_search
from bot.tools.voice_handler import process_voice_message
from bot.models import create_db_and_tables, get_session, User, Message

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Gestionnaire de messages vocaux
@dp.message(lambda message: message.voice is not None)
async def voice_message_handler(message: types.Message):
    """Traite les messages vocaux et les transcrit."""
    try:
        # Traite le message vocal
        transcription = await process_voice_message(bot, message)
        if transcription:
            logging.info(f"Transcription reçue: {transcription}")
            
            # Enregistre le message dans la base de données
            session = next(get_session())
            user = User.get_or_create(
                session,
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code
            )
            Message.add_message(session, user.id, transcription, is_from_user=True)
            
            # Traite la transcription comme un message textuel avec l'agent mémoire
            answer = process_message_with_memory(message.from_user.id, transcription, session)
            
            # Enregistre la réponse du bot
            Message.add_message(session, user.id, answer, is_from_user=False)
            
            # Envoie la réponse en tant que nouveau message
            await message.answer(answer)
    except Exception as e:
        logging.error(f"Erreur dans le gestionnaire de messages vocaux: {str(e)}")
        await message.reply("Désolé, une erreur s'est produite lors du traitement de votre message vocal.")

@dp.message()
async def root_handler(message: types.Message):
    """Redirige le texte utilisateur vers l'agent."""
    if not message.text:
        await message.answer("Je ne comprends que le texte pour l'instant.")
        return
    
    user_input = message.text
    
    # Enregistre l'utilisateur et le message dans la base de données
    session = next(get_session())
    user = User.get_or_create(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code
    )
    Message.add_message(session, user.id, user_input, is_from_user=True)
    
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
                response = f"Voici les résultats pour '{query}':"
                
                # Enregistre la réponse du bot
                Message.add_message(session, user.id, response, is_from_user=False)
                await message.answer(response)
                
                # Envoie les résultats en plusieurs messages si nécessaire
                for i, result in enumerate(results[:5]):
                    result_text = f"{i+1}. {result}"
                    Message.add_message(session, user.id, result_text, is_from_user=False)
                    await message.answer(result_text)
                return
            except Exception as e:
                error_msg = f"Désolé, je n'ai pas pu effectuer la recherche : {str(e)}"
                Message.add_message(session, user.id, error_msg, is_from_user=False)
                await message.answer(error_msg)
                return
    
    # Sinon, traite normalement avec l'agent mémoire
    answer = process_message_with_memory(message.from_user.id, user_input, session)
    
    # Enregistre la réponse du bot
    Message.add_message(session, user.id, answer, is_from_user=False)
    
    await message.answer(answer)


# Application FastAPI
app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    """Configure le webhook Telegram et initialise la base de données."""
    # Initialisation de la base de données
    create_db_and_tables()
    logging.info("Base de données initialisée")
    
    # Configuration du webhook Telegram
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


# Endpoint pour récupérer l'historique des messages d'un utilisateur
@app.get("/api/history/{telegram_id}")
async def get_user_history(telegram_id: int, session: Session = Depends(get_session)):
    """Récupère l'historique des messages d'un utilisateur."""
    user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        return {"error": "Utilisateur non trouvé"}
    
    messages = session.exec(select(Message).where(Message.user_id == user.id).order_by(Message.created_at)).all()
    return {
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username
        },
        "messages": [
            {
                "id": msg.id,
                "text": msg.text,
                "is_from_user": msg.is_from_user,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


# Ajout du mode polling pour les tests locaux
if __name__ == "__main__":
    logging.info("Bot démarré en mode polling")
    import asyncio
    asyncio.run(dp.start_polling(bot)) 