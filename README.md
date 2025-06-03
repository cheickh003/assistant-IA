# Assistant IA Telegram

Ce dépôt contient un assistant IA complet basé sur FastAPI, aiogram 3, LangChain et divers outils Google.

## Installation locale

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.template .env
# Éditez .env et renseignez vos clés
uvicorn bot.main:app --reload
```

## Déploiement Docker

```bash
docker build -t assistant-ia .
docker run -p 8080:8080 --env-file .env assistant-ia
```

## Fonctionnalités

* Dialogue naturel via Telegram
* Envoi d'e-mails (Gmail)
* Gestion d'événements Google Calendar
* Prise de notes et recherche Web
* Transcription vocale (Whisper)

Reportez-vous à `docs/projet.md` pour la conception détaillée. 