from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Session, create_engine, select
import os

# URL de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@postgres:5432/assistant_ia")

# Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL)

class User(SQLModel, table=True):
    """Modèle représentant un utilisateur du bot."""
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(index=True, unique=True)
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    messages: List["Message"] = Relationship(back_populates="user")
    notes: List["Note"] = Relationship(back_populates="user")
    
    @classmethod
    def get_or_create(cls, session: Session, telegram_id: int, **kwargs):
        """Récupère un utilisateur existant ou en crée un nouveau."""
        user = session.exec(select(cls).where(cls.telegram_id == telegram_id)).first()
        if not user:
            user = cls(telegram_id=telegram_id, **kwargs)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

class Message(SQLModel, table=True):
    """Modèle représentant un message de conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    text: str
    is_from_user: bool = True  # True si de l'utilisateur, False si du bot
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    user: User = Relationship(back_populates="messages")
    
    @classmethod
    def add_message(cls, session: Session, user_id: int, text: str, is_from_user: bool = True):
        """Ajoute un nouveau message à la base de données."""
        message = cls(user_id=user_id, text=text, is_from_user=is_from_user)
        session.add(message)
        session.commit()
        return message

class Note(SQLModel, table=True):
    """Modèle représentant une note utilisateur."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    user: User = Relationship(back_populates="notes")
    
    @classmethod
    def add_note(cls, session: Session, user_id: int, content: str):
        """Ajoute une nouvelle note à la base de données."""
        note = cls(user_id=user_id, content=content)
        session.add(note)
        session.commit()
        return note
    
    @classmethod
    def get_user_notes(cls, session: Session, user_id: int):
        """Récupère toutes les notes d'un utilisateur."""
        return session.exec(select(cls).where(cls.user_id == user_id).order_by(cls.created_at.desc())).all()

# Création des tables au démarrage
def create_db_and_tables():
    """Crée la base de données et les tables si elles n'existent pas."""
    SQLModel.metadata.create_all(engine)

# Fonction pour obtenir une session de base de données
def get_session():
    """Retourne une session de base de données."""
    with Session(engine) as session:
        yield session 