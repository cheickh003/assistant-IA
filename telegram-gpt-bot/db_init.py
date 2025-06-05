import sqlite3, os
from dotenv import load_dotenv

load_dotenv()
db_path = os.getenv("SQLITE_PATH", "memory.db")

con = sqlite3.connect(db_path)
cur = con.cursor()

# Charge l'extension vec0 ― nécessite sqlite ≥3.45 compilé --enable-load-extension
cur.execute("SELECT load_extension('sqlite_vec')")  # nom .so installé par `pip install sqlite-vec`
# Table messages (texte brut)
cur.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    role TEXT,
    content TEXT,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
# Table embeddings (vec0)
cur.execute("""
CREATE VIRTUAL TABLE IF NOT EXISTS embeddings
USING vec0(id INTEGER PRIMARY KEY, vec BLOB(1536))
""")
con.commit()
con.close() 