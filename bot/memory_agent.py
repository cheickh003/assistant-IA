import os
import re
import logging
from openai import OpenAI
from bot.config import OPENAI_API_KEY
from bot.models import User, UserMemory, get_session
from sqlmodel import Session

# Initialisation du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Expressions régulières pour détecter quand l'utilisateur veut se présenter
NAME_PATTERNS = [
    r"(?:je|j')(?:\s+me?)?(?:\s+nomme|'appelle|suis)\s+(\w+)",
    r"mon\s+(?:nom\s+(?:est|c'est)|prénom\s+(?:est|c'est))\s+(\w+)",
]

# Expressions régulières pour détecter quand l'utilisateur veut mémoriser son nom
REMEMBER_PATTERNS = [
    r"(?:souviens|rappelle|retiens|mémorise)[\s-]+toi\s+(?:de|que|du|mon)\s+(?:mon\s+nom|moi|prénom|je\s+m'appelle)\s+(?:est|comme)?\s+(\w+)",
    r"(?:enregistre|sauvegarde|stocke|garde)\s+(?:mon\s+nom|prénom|que\s+je\s+m'appelle)\s+(?:est|comme)?\s+(\w+)",
    r"(?:enregistre|sauvegarde|stocke|garde|souviens|rappelle)\s+(?:le|ça|mon\s+nom|que\s+je\s+m'appelle\s+)?\s*(\w+)",
]

def extract_name(text):
    """Tente d'extraire un nom d'utilisateur à partir du texte."""
    # Vérifier les patterns de présentation
    for pattern in NAME_PATTERNS:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).strip().capitalize()
    
    # Vérifier les patterns de mémorisation
    for pattern in REMEMBER_PATTERNS:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).strip().capitalize()
    
    return None

def check_name_request(text):
    """Vérifie si l'utilisateur demande comment il s'appelle."""
    patterns = [
        r"comment\s+(?:je|j')\s*(?:me)?\s*(?:nomme|appelle|'appelle)",
        r"(?:quel|tu connais)\s+(?:est)?\s*mon\s+(?:nom|prénom)",
        r"je\s+m'appelle\s+comment",
    ]
    
    for pattern in patterns:
        if re.search(pattern, text.lower()):
            return True
    
    return False

class MemoryAgent:
    """Agent avec mémoire persistante."""
    
    def __init__(self):
        self.client = client
    
    def process_message(self, user_id, user_input, session=None):
        """Traite un message utilisateur avec mémoire persistante."""
        # Obtenir une session si non fournie
        if session is None:
            session = next(get_session())
        
        try:
            # Récupérer l'utilisateur et sa mémoire
            user = User.get_or_create(session, telegram_id=user_id)
            memory = UserMemory.get_or_create(session, user.id)
            
            # Mettre à jour l'heure de dernière interaction
            user.update_interaction(session)
            
            # Vérifier si l'utilisateur demande son nom
            if check_name_request(user_input):
                name = memory.get_name()
                if name:
                    return f"D'après mes souvenirs, tu t'appelles {name}."
                else:
                    return "Je ne connais pas ton nom. Si tu veux, tu peux me le dire !"
            
            # Essayer d'extraire un nom si l'utilisateur se présente
            name = extract_name(user_input)
            if name:
                # Mémoriser le nom
                memory.remember_name(session, name)
                return f"Ravi de te rencontrer, {name}! Je me souviendrai de ton nom."
            
            # Construire le contexte pour l'API
            system_message = "Tu es un assistant IA utile qui répond en français. "
            
            # Ajouter le nom de l'utilisateur au contexte s'il est connu
            known_name = memory.get_name()
            if known_name:
                system_message += f"L'utilisateur s'appelle {known_name}. Utilise son nom occasionnellement pour personnaliser tes réponses. "
            
            system_message += "Tu peux aider avec des recherches web, prendre des notes, et planifier des événements. Si l'utilisateur te demande de chercher quelque chose sur Internet, indique que tu peux le faire grâce à SerpAPI."
            
            # Appel à l'API OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Erreur dans memory_agent.process_message: {str(e)}")
            return f"Désolé, je n'ai pas pu traiter votre message : {str(e)}"

# Créer une instance unique de l'agent
memory_agent = MemoryAgent()

def process_message_with_memory(user_id, user_input, session=None):
    """Fonction utilitaire pour traiter un message avec l'agent mémoire."""
    return memory_agent.process_message(user_id, user_input, session) 