import os
from openai import OpenAI
from bot.config import OPENAI_API_KEY

# Initialisation du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def process_message(user_input):
    """
    Traite un message utilisateur avec l'API OpenAI directement.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant IA utile qui répond en français. Tu peux aider avec des recherches web, prendre des notes, et planifier des événements. Si l'utilisateur te demande de chercher quelque chose sur Internet, indique que tu peux le faire grâce à SerpAPI."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Désolé, je n'ai pas pu traiter votre message : {str(e)}" 