import os, asyncio, sqlite3
from langchain_community.vectorstores import SQLiteVec
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
db_path = os.getenv("SQLITE_PATH", "memory.db")
connection_string = f"sqlite:///{db_path}"

# Historique textuel
def chat_history(chat_id: int):
    return SQLChatMessageHistory(
        session_id=str(chat_id),
        connection_string=connection_string,
    )

# Vector store  (utilise la table embeddings déjà créée)
vec_store = SQLiteVec(
    db_path,
    table_name="embeddings",
    embedding_function=OpenAIEmbeddings(
        model=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    ),
)

# Mémoire smart : 4 k tokens max, le reste résumé
def summary_memory(history):
    return ConversationSummaryBufferMemory(
        llm=None,  # sera injecté plus tard
        chat_memory=history,
        max_token_limit=4096
    ) 