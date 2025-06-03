from typing import Any
from serpapi import GoogleSearch
from bot.config import SERPAPI_KEY

# Les fonctions ci-dessous seront complétées ultérieurement.

def send_email(to: str, subject: str, body: str) -> str:
    """Envoie un e-mail via l'API Gmail. Stub pour l'instant."""
    # TODO: Implémenter l'appel à Gmail API
    return "Email envoyé (simulation)."

def add_event(summary: str, start: str, end: str) -> str:
    """Ajoute un événement Google Calendar. Stub pour l'instant."""
    # TODO: Implémenter l'appel à Calendar API
    return "Événement créé (simulation)."

def web_search(query: str, num: int = 5) -> list[str]:
    """Recherche Web via SerpApi ou DuckDuckGo. Stub."""
    try:
        # Utilise SerpApi pour la recherche Google
        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num,
            "hl": "fr"  # Langue française pour les résultats
        })
        results = search.get_dict()
        
        if "organic_results" in results:
            # Format: titre + lien + extrait
            return [f"{r.get('title', 'Sans titre')} - {r.get('link', '#')} \n{r.get('snippet', 'Pas de description')}" 
                   for r in results["organic_results"][:num]]
        else:
            return [f"Aucun résultat trouvé pour '{query}'"]
    except Exception as e:
        return [f"Erreur lors de la recherche: {str(e)}"]

def add_note(text: str) -> str:
    """Ajoute une note à la base PostgreSQL. Stub."""
    # TODO: Insérer en base avec un user_id fixe pour le moment
    user_id = 1  # ID utilisateur par défaut pour le moment
    return f"Note enregistrée (simulation) : {text}"

def list_notes() -> list[Any]:
    """Liste les notes de l'utilisateur. Stub."""
    # TODO: Requêter la base avec un user_id fixe pour le moment
    user_id = 1  # ID utilisateur par défaut pour le moment
    return ["Note 1", "Note 2"] 