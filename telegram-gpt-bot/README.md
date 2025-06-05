# Telegram GPT Bot avec mémoire vectorielle

Bot Telegram intelligent avec mémoire conversationnelle et vectorielle basé sur GPT-4o Mini et SQLiteVec.

## Caractéristiques

- **100% Local** : Stockage dans SQLite avec l'extension sqlite-vec pour les embeddings
- **Mémoire vectorielle** : Recherche sémantique dans les conversations passées
- **Optimisation des coûts** : Résumés automatiques des anciennes conversations
- **Facile à déployer** : Service systemd prêt à l'emploi

## Prérequis

- Python 3.10+
- SQLite 3.45+ (avec support des extensions)
- Extension sqlite-vec installée
- Compte Telegram Bot
- Clé API OpenAI

## Installation rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-org/telegram-gpt-bot.git
cd telegram-gpt-bot

# 2. Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp .env.example .env
# Modifier .env avec vos clés API

# 4. Initialiser la base de données
python db_init.py

# 5. Lancer le bot
python bot.py
```

## Déploiement avec systemd

```bash
sudo cp -r . /opt/telegram-gpt-bot
sudo useradd -r botuser
sudo chown -R botuser:botuser /opt/telegram-gpt-bot
sudo systemctl enable /opt/telegram-gpt-bot/service/telegrambot.service
sudo systemctl start telegrambot
```

## Maintenance

### Sauvegarde

```bash
sqlite3 memory.db ".backup 'backup-$(date +%F).db'"
```

### Surveillance

```bash
journalctl -u telegrambot -f
```

### Optimisation

En cas de besoin de reconstruire l'index vectoriel:

```bash
sqlite3 memory.db "INSERT INTO embeddings(embeddings) VALUES('rebuild');"
```

## Architecture

- **db_init.py** : Initialisation de la base SQLite avec l'extension vec0
- **embeddings.py** : Wrapper pour l'API OpenAI Embeddings
- **memory.py** : Gestion de l'historique de conversation et du stockage vectoriel
- **handlers.py** : Logique de traitement des messages Telegram
- **bot.py** : Point d'entrée du bot

## Licence

MIT 