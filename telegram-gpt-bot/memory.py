import os
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("SQLITE_PATH", "bot_memory.db")
CONNECTION_STRING = f"sqlite:///{DB_PATH}"
TABLE_NAME = "message_history"

def get_chat_history(chat_id: int) -> SQLChatMessageHistory:
    """
    Retourne un objet pour interagir avec l'historique de chat
    d'un utilisateur spécifique dans la base de données SQLite.
    """
    return SQLChatMessageHistory(
        session_id=str(chat_id),
        connection_string=CONNECTION_STRING,
        table_name=TABLE_NAME,
    )

def get_summary_memory(history: SQLChatMessageHistory) -> ConversationSummaryBufferMemory:
    """
    Crée une mémoire qui résume les anciens messages pour
    contrôler la taille du contexte envoyé au LLM.
    
    Note: Un LLM est requis pour effectuer le résumé. Nous utilisons
    le modèle principal ici, mais un modèle plus rapide/économique
    pourrait être envisagé pour cette tâche.
    """
    summarizer_llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
    )

    return ConversationSummaryBufferMemory(
        llm=summarizer_llm,
        chat_memory=history,
        max_token_limit=3500, # Garde une marge pour le prompt et la réponse
        return_messages=True, # Important pour le prompt
    ) 