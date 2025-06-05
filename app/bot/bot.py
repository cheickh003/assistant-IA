import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from sqlalchemy.orm import Session

from app.config import BOT_TOKEN
from app.database.models import get_db
from app.database.chat_repository import get_or_create_user, save_message, get_chat_history
from app.services.ai_service import get_ai_response

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation du bot et du dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """Gestionnaire pour la commande /start"""
    user_full_name = message.from_user.full_name
    await message.answer(f"Bonjour, {user_full_name}! Je suis votre assistant IA.\n\nVous pouvez me poser des questions ou discuter avec moi. J'ai une mémoire et je me souviendrai de notre conversation.")

    # Enregistrer l'utilisateur dans la base de données
    db = next(get_db())
    get_or_create_user(
        db=db,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

@dp.message()
async def message_handler(message: types.Message) -> None:
    """Gestionnaire pour tous les messages textuels"""
    # Obtenir l'ID Telegram de l'utilisateur
    telegram_id = message.from_user.id
    user_message = message.text

    # Message d'attente pendant que l'IA réfléchit
    await message.answer("Je réfléchis...")

    try:
        # Obtenir la session de base de données
        db = next(get_db())

        # Récupérer ou créer l'utilisateur
        user = get_or_create_user(
            db=db,
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

        # Enregistrer le message de l'utilisateur
        save_message(db=db, user_id=user.id, content=user_message, role="user")

        # Récupérer l'historique des messages
        chat_history = get_chat_history(db=db, user_id=user.id, limit=10)

        # Formater l'historique pour l'IA
        formatted_history = []
        for msg in reversed(chat_history):
            formatted_history.append({"role": msg.role, "content": msg.content})

        # Obtenir la réponse de l'IA
        ai_response = await get_ai_response(user_message, formatted_history)

        # Enregistrer la réponse de l'IA
        save_message(db=db, user_id=user.id, content=ai_response, role="assistant")

        # Envoyer la réponse à l'utilisateur
        await message.answer(ai_response)

    except Exception as e:
        logger.error(f"Erreur lors du traitement du message: {e}")
        await message.answer("Désolé, une erreur s'est produite lors du traitement de votre demande.")
