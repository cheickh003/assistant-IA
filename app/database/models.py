from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from app.config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="user")

    def __repr__(self):
        return f"<User {self.telegram_id}>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="messages")
    role = Column(String(50), default="user")  # 'user' ou 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id}: {self.role}>"

# Initialisation de la base de données
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Crée les tables dans la base de données"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Fournit une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
