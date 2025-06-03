#!/usr/bin/env python3
"""
Script de migration pour modifier le type de la colonne telegram_id de INTEGER à BIGINT
"""
import os
import sys
import sqlalchemy as sa
from sqlalchemy import create_engine, text

# URL de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgrespassword@postgres:5432/assistant_ia")

def migrate():
    """Exécute la migration de la base de données."""
    print("Démarrage de la migration de la base de données...")
    
    # Connexion à la base de données
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        print("Connexion à la base de données établie.")
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        sys.exit(1)
    
    try:
        # Vérifier si la table user existe
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')"))
        table_exists = result.scalar()
        
        if not table_exists:
            print("La table 'user' n'existe pas. Aucune migration nécessaire.")
            return
        
        # Début de la transaction
        trans = conn.begin()
        
        # Modifier le type de la colonne telegram_id
        print("Modification du type de la colonne telegram_id de INTEGER à BIGINT...")
        conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN telegram_id TYPE BIGINT"))
        
        # Confirmer la transaction
        trans.commit()
        print("Migration terminée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        if 'trans' in locals() and trans.is_active:
            trans.rollback()
            print("Transaction annulée.")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate() 