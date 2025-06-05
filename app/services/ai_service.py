import logging
import openai
from typing import List, Dict, Any

from app.config import OPENAI_API_KEY

# Configuration du client OpenAI
openai.api_key = OPENAI_API_KEY

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ai_response(message: str, chat_history: List[Dict[str, str]]) -> str:
    """Obtient une réponse de l'IA en utilisant l'API OpenAI"""
    try:
        # Si pas d'historique ou historique vide, initialiser avec un message système
        if not chat_history:
            chat_history = [{
                "role": "system", 
                "content": "Vous êtes un assistant IA utile et amical qui aide l'utilisateur. Soyez concis mais informatif dans vos réponses."
            }]
        else:
            # Insérer le message système au début si ce n'est pas déjà le cas
            if chat_history[0]["role"] != "system":
                chat_history.insert(0, {
                    "role": "system", 
                    "content": "Vous êtes un assistant IA utile et amical qui aide l'utilisateur. Soyez concis mais informatif dans vos réponses."
                })

        # Ajouter le nouveau message de l'utilisateur
        chat_history.append({"role": "user", "content": message})

        # Appel à l'API OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Modèle moins cher et plus rapide pour commencer
            messages=chat_history,
            max_tokens=500
        )

        # Extraire et retourner la réponse
        ai_response = response.choices[0].message.content
        return ai_response

    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {e}")
        return "Désolé, je rencontre des difficultés à générer une réponse pour le moment."
