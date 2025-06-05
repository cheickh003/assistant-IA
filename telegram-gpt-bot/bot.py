import asyncio, os, logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters
)
from handlers import chat
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    app = (
        ApplicationBuilder()
        .token(os.getenv("TELEGRAM_TOKEN"))
        .build()
    )

    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Salut !")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main()) 