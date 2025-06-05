import os, asyncio
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()
embedder = OpenAIEmbeddings(
    model=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

async def get_embedding(text: str) -> list[float]:
    # LangChain gère déjà l'appel asynchrone interne
    return await embedder.aembed_query(text) 