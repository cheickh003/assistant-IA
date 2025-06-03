from typing import Any

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
    # TODO: Implémenter la recherche réelle
    return [f"Résultat {i+1} pour '{query}'" for i in range(num)]

def add_note(user_id: int, text: str) -> str:
    """Ajoute une note à la base PostgreSQL. Stub."""
    # TODO: Insérer en base
    return "Note enregistrée (simulation)."

def list_notes(user_id: int) -> list[Any]:
    """Liste les notes de l'utilisateur. Stub."""
    # TODO: Requêter la base
    return ["Note 1", "Note 2"] 