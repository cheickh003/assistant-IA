#!/usr/bin/env python3
"""
Script de migration simple pour modifier le type de la colonne telegram_id de INTEGER à BIGINT
Utilise directement psycopg2 au lieu de SQLAlchemy
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

# URL de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@postgres:5432/assistant_ia")

def parse_db_url(url):
    """Parse l'URL de la base de données pour extraire les paramètres de connexion."""
    parsed = urlparse(url)
    return {
        'dbname': parsed.path[1:],
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 5432
    }

def migrate():
    """Exécute la migration de la base de données."""
    print("Démarrage de la migration de la base de données (version simple)...")
    
    # Paramètres de connexion
    db_params = parse_db_url(DATABASE_URL)
    
    # Connexion à la base de données
    try:
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True  # Pour éviter les problèmes de transaction
        cursor = conn.cursor()
        print("Connexion à la base de données établie.")
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        sys.exit(1)
    
    try:
        # Vérifier si la table user existe
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')")
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("La table 'user' n'existe pas. Aucune migration nécessaire.")
            return
        
        # Modifier le type de la colonne telegram_id
        print("Modification du type de la colonne telegram_id de INTEGER à BIGINT...")
        cursor.execute('ALTER TABLE "user" ALTER COLUMN telegram_id TYPE BIGINT')
        
        print("Migration terminée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate() 