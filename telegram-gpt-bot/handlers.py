from telegram import Update
from telegram.ext import ContextTypes

from memory import chat_history, summary_memory, vec_store
from embeddings import get_embedding
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)

PROMPT = PromptTemplate.from_template(
    """Tu es un assistant IA. Voici le contexte récupéré : {vectors}
Historique récent : {history}
Utilisateur : {user_input}
Assistant :"""
)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    cid = update.effective_chat.id

    # 1) Récupère historique brut
    hist = chat_history(cid)
    # 2) Récupère messages sémantiquement proches
    q_embed = await get_embedding(txt)
    vectors = vec_store.similarity_search_by_vector(q_embed, k=5, metadata_filter={"chat_id": cid})

    memory = summary_memory(hist)
    chain = LLMChain(llm=llm, prompt=PROMPT, memory=memory)

    answer = await chain.arun(
        vectors="\n".join([d.page_content for d in vectors]),
        user_input=txt
    )

    await update.message.reply_text(answer)

    # 3) Persiste texte + embedding
    hist.add_user_message(txt)
    hist.add_ai_message(answer)
    vec_store.add_texts([txt, answer], ids=[None, None], metadatas=[{"chat_id": cid}]*2) 