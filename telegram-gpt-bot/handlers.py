import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from memory import get_chat_history, get_summary_memory

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation du LLM
try:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
    )
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation du LLM de OpenAI: {e}")
    llm = None

# Prompt simplifié qui utilise l'historique de la mémoire
PROMPT_TEMPLATE = """Tu es un assistant IA conversationnel. Réponds à la question de l'utilisateur en te basant sur l'historique de la conversation.

Historique de la conversation:
{history}

Utilisateur: {input}
Assistant:"""

PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=PROMPT_TEMPLATE
)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les messages texte des utilisateurs."""
    if not llm:
        await update.message.reply_text("Désolé, le service IA n'est pas correctement configuré. Veuillez contacter l'administrateur.")
        return

    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    # Indique que le bot est en train d'écrire
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')

    try:
        # 1. Récupérer l'historique et la mémoire associée
        history = get_chat_history(chat_id)
        memory = get_summary_memory(history)

        # 2. Créer et exécuter la chaîne LangChain
        # La mémoire (historique + résumé) est gérée automatiquement
        chain = LLMChain(llm=llm, prompt=PROMPT, memory=memory, verbose=False)
        
        # 'arun' est pratique pour un seul input/output.
        answer = await chain.arun(input=user_text)

        # 3. Envoyer la réponse et la sauvegarder dans l'historique
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Erreur lors du traitement du message pour le chat_id {chat_id}: {e}")
        await update.message.reply_text("Oups, une erreur est survenue. Veuillez réessayer.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère la commande /start."""
    start_message = "Bonjour ! Je suis votre assistant IA personnel.\n\nEnvoyez-moi un message et je ferai de mon mieux pour vous répondre. Ma mémoire est persistante, je me souviendrai de nos conversations précédentes."
    await update.message.reply_text(start_message) 