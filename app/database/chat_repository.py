from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.models import User, Message

def get_or_create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
    """Récupère un utilisateur existant ou en crée un nouveau"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

def save_message(db: Session, user_id: int, content: str, role: str = "user") -> Message:
    """Sauvegarde un message dans la base de données"""
    message = Message(user_id=user_id, content=content, role=role)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_chat_history(db: Session, user_id: int, limit: int = 10) -> List[Message]:
    """Récupère l'historique des messages d'un utilisateur"""
    return db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.desc()).limit(limit).all()
