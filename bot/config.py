import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GMAIL_CLIENT_SECRET_FILE: str = os.getenv("GMAIL_CLIENT_SECRET_FILE", "credentials.json")
GOOGLE_PROJECT: str = os.getenv("GOOGLE_PROJECT", "")
SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
WEB_URL: str = os.getenv("WEB_URL", "") 