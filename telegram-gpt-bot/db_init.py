import sqlite3
import os
from dotenv import load_dotenv

# Charge les variables d'environnement du fichier .env
load_dotenv()

DB_PATH = os.getenv("SQLITE_PATH", "bot_memory.db")

def main():
    """
    Crée le fichier de base de données SQLite s'il n'existe pas.
    LangChain s'occupera de créer la table nécessaire au premier lancement.
    Ce script sert simplement à confirmer que le fichier .db est prêt.
    """
    print("Vérification de la base de données...")
    try:
        # La simple connexion crée le fichier s'il est manquant.
        con = sqlite3.connect(DB_PATH)
        con.close()
        print(f"Base de données prête à l'emplacement : {DB_PATH}")
        print("La table pour l'historique des messages sera créée automatiquement par LangChain au premier usage.")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")

if __name__ == "__main__":
    main() 