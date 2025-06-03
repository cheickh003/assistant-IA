import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GMAIL_CLIENT_SECRET_FILE: str = os.getenv("GMAIL_CLIENT_SECRET_FILE", "credentials.json")
GOOGLE_PROJECT: str = os.getenv("GOOGLE_PROJECT", "")
SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "719558b3c3cc0f95589c4eeb98a2f961dfff11ed930f3528fc5e1a4af597f328")
WEB_URL: str = os.getenv("WEB_URL", "") 