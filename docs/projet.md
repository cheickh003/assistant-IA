## 1. Architecture globale

### 1.1 Couche interface : Bot Telegram

* Créez un bot via **@BotFather** pour obtenir le `BOT_TOKEN`.
* Utilisez **aiogram 3** (asynchrone, typé, support complet de toutes les méthodes API) pour recevoir / envoyer messages, documents, voix et inline-queries ([docs.aiogram.dev][1]).
* Déclarez trois types de handlers : `MessageHandler` (texte), `MessageHandler` (audio/voice), `CallbackQueryHandler` (boutons).

### 1.2 Couche logique IA : Agent LangChain

* **LangChain** permet d’assembler un *agent* alimenté par GPT-4o et enrichi d’outils Python (« Tools ») : `EmailTool`, `CalendarTool`, `SearchTool`, `NotesTool`.
* Exemple de bot agentique utilisant ces tools dans n8n ([n8n.io][12]) et documentation d’intégration Telegram dans LangChain ([python.langchain.com][13]).

### 1.3 Outils (Tools)

| Besoin            | Outil concret                                                                                             | Détail API                                                     |
| ----------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **E-mail**        | Gmail API ou SMTP                                                                                         | OAuth 2.0 + `users.messages.send` ([Google for Developers][5]) |
| **Agenda**        | Google Calendar API                                                                                       | `events.insert` ([Google for Developers][7])                   |
| **Recherche Web** | SerpApi (`google-search-results`) ([SerpApi][8]) ou DuckDuckGo Instant Answer ([Postman API Platform][9]) |                                                                |
| **Notes**         | SQLModel + PostgreSQL pour méta-données ; fichier Markdown persistant (Cloudflare R2)                     |                                                                |
| **Voix**          | `faster-whisper` local ou API OpenAI Whisper ([PyPI][3])                                                  |                                                                |

### 1.4 Backend FastAPI

* Gère webhooks Telegram, endpoints OAuth Google, stockage Notes, file-download voix.
* Expose un endpoint `/webhook/{token}` que vous déclarez dans `setWebhook`.

### 1.5 Files d’attente & background jobs

* **Celery + Redis** pour tâches longues (transcription, envoi d’e-mails) afin de ne pas bloquer la réponse Telegram.
* Chaque tâche termine en poussant un message vers LangChain Tool ou directement vers l’API Telegram.

---

## 2. Choix techniques et dépendances

| Domaine       | Lib / Service recommandé                                                          | Pourquoi                                          |
| ------------- | --------------------------------------------------------------------------------- | ------------------------------------------------- |
| Telegram      | `aiogram==3.*`                                                                    | Typage Pydantic, gestion FSM, middlewares         |
| HTTP / ASGI   | FastAPI + Uvicorn                                                                 | Haute perf, annotations, Webhook HTTPS            |
| LLM / Agent   | `langchain`, `openai`                                                             | Orchestration d’outils, mémoire conversationnelle |
| Transcription | `faster-whisper`                                                                  | CPU/GPU locaux, rapide ([PyPI][3])                |
| E-mail        | `google-api-python-client` + Gmail API quickstart ([Google for Developers][4])    |                                                   |
| Agenda        | `google-api-python-client` + Calendar API quickstart ([Google for Developers][6]) |                                                   |
| Recherche     | `google-search-results` (SerpApi) ([SerpApi][8])                                  |                                                   |
| DB            | SQLModel (PostgreSQL)                                                             | ORM + dataclasses, migrations Alembic             |
| Files         | Cloudflare R2 ou local FS                                                         | Stocker `.md` et audio                            |
| Queue         | Celery + Redis                                                                    | Asynchrone, planification                         |

---

## 3. Implémentation pas à pas

### 3.1 Initialisation du projet

```bash
python -m venv venv && source venv/bin/activate
pip install aiogram fastapi uvicorn[standard] langchain openai \
            google-api-python-client google-auth-oauthlib google-auth-httplib2 \
            celery redis sqlmodel psycopg2-binary faster-whisper python-dotenv \
            google-search-results duckduckgo-search
```

Créez `.env` pour vos clés :

```
BOT_TOKEN=...
OPENAI_API_KEY=...
GMAIL_CLIENT_SECRET_FILE=credentials.json
GOOGLE_PROJECT=...
SERPAPI_KEY=...
```

### 3.2 Bot de base

```python
from aiogram import Bot, Dispatcher, types

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def root_handler(msg: types.Message):
    answer = agent.invoke(msg.text)   # agent = LangChain Agent
    await msg.answer(answer)

async def on_startup():
    await bot.set_webhook(f"{WEB_URL}/webhook/{BOT_TOKEN}")

app = FastAPI(on_startup=[on_startup])
app.post(f"/webhook/{BOT_TOKEN}")(dp.as_handler())
```

Doc API Bot ([docs.aiogram.dev][14]).

### 3.3 Traitement des messages vocaux

1. Téléchargez le fichier OGG via `bot.download_file`.
2. Convertissez en WAV : `ffmpeg -i input.ogg output.wav`.
3. Transcrivez :

```python
from faster_whisper import WhisperModel
model = WhisperModel("base")
segments, _ = model.transcribe("output.wav")
text = " ".join([s.text for s in segments])
```

Exemple complet de bot de transcription ([GitHub][15]).

### 3.4 Envoi d’e-mail

```python
service = build("gmail", "v1", credentials=creds)  # OAuth flow
message = MIMEText(body, "plain")
message["to"] = to_addr
message["subject"] = subject
raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
service.users().messages().send(userId="me", body={"raw": raw}).execute()
```

Guide `messages.send` ([Google for Developers][5]).

### 3.5 Ajout d’un événement calendrier

```python
event = {
  "summary": "Réunion projet",
  "start": {"dateTime": "2025-06-05T09:00:00", "timeZone": "Africa/Abidjan"},
  "end":   {"dateTime": "2025-06-05T10:00:00", "timeZone": "Africa/Abidjan"}
}
calendar.events().insert(calendarId="primary", body=event).execute()
```

Méthode `events.insert` ([Google for Developers][7]).

### 3.6 Recherche Web

```python
from serpapi import GoogleSearch
search = GoogleSearch({"q": query, "api_key": SERPAPI_KEY, "num": 5})
results = search.get_dict()
links = [r["link"] for r in results["organic_results"]]
```

SerpApi Python intégration ([SerpApi][8]).
Si vous préférez gratuit : requête HTTP GET `https://api.duckduckgo.com/?q=texte&format=json` ([Postman API Platform][9]).

### 3.7 Prise de notes

* Table `notes(id, user_id, text, created_at)`.
* Chaque transcription ou message marqué « note » s’enregistre.
* Commandes `/notes` (liste) et `/note <id>` (affiche / exporte).

---

## 4. Orchestration IA : LangChain Agent

```python
from langchain.agents import initialize_agent, Tool
tools = [
   Tool.from_function(send_email, name="send_email"),
   Tool.from_function(add_event, name="add_event"),
   Tool.from_function(web_search, name="search_web"),
   Tool.from_function(add_note, name="add_note"),
   Tool.from_function(list_notes, name="list_notes"),
]
agent = initialize_agent(
    tools, llm=ChatOpenAI(model="gpt-4o-mini"), agent="chat-zero-shot-react-description"
)
```

L’agent lit la consigne (« quand l’utilisateur demande X, appelle tel tool ») et renvoie la réponse enrichie.

---

## 5. Sécurité et conformité

1. **OAuth** : tokens Gmail / Calendar stockés chiffrés (AES-256) en base ou Secret Manager.
2. **Webhooks** Telegram : utilisez HTTPS (Let’s Encrypt) ou Cloudflare Tunnel.
3. **Rate limits** OpenAI : implémentez un throttling Celery / Redis.
4. **GDPR** : offrez `/delete_account` pour anonymiser données.

---

## 6. Déploiement conteneurisé

### 6.1 Dockerfile FastAPI

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "bot.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Tutoriel officiel Docker FastAPI ([fastapi.tiangolo.com][11]).

### 6.2 Fly.io (ou Railway)

```bash
flyctl launch --name my-ai-assistant --dockerfile Dockerfile
flyctl secrets set BOT_TOKEN=... OPENAI_API_KEY=...
flyctl deploy
```

Guide officiel FastAPI sur Fly.io ([fly.io][10]) et article déploiement pas-à-pas ([Pybites][16]).

Fly propose un volume Postgres, un add-on Redis et un certificat TLS gratuit. Alternative : conteneur Docker sur AWS ECS / Lightsail ([Reddit][17]).

---

## 7. Coûts & performances

| Composant            | Gratuit             | Payant                      |
| -------------------- | ------------------- | --------------------------- |
| Telegram Bot         | ✅                   | –                           |
| Fly.io (<= 3 Go RAM) | ✅ (alloc. gratuite) | \~5 \$ USD/mois au-delà     |
| OpenAI GPT-4o        | –                   | \~0,005 \$ / 1 k tokens     |
| Whisper local        | ✅ (si GPU)          | GPU cloud si usage intensif |
| SerpApi              | 100 queries/jour    | 50 \$/mois illimité         |
| Google APIs          | 2 000 req/jour     | tarif Google Cloud          |

---

## 8. Évolution future

1. **LLM local** : Llama 3 70B quantisé (gguf) + Ollama pour réduire coûts.
2. **Notes multimédia** : génération résumés vocaux inverses (TTS) pour lecture.
3. **Gestion multi-utilisateurs** avec SSO Google / Telegram login.
4. **Tableau de bord** Streamlit ou Next.js pour visualiser tâches et notes.
5. **Intégration Notion / Obsidian** via API pour pousser ou tirer vos notes.

---

## 9. Checklist rapide à exécuter

1. ✅ Créer le bot Telegram & récupérer `BOT_TOKEN`.
2. ✅ Activer Gmail API & Calendar API dans Google Cloud Console ; télécharger `credentials.json`.
3. ✅ Cloner votre repo Git, ajouter Dockerfile, `.env`, `requirements.txt`.
4. ✅ Implémenter handlers aiogram + agent LangChain + tools.
5. ✅ Tester en local (`ngrok` ou Cloudflare Tunnel) et vérifier webhook.
6. ✅ Docker build & `flyctl launch`.
7. ✅ Configurer Redis & Postgres sur Fly.io.
8. ✅ Mettre en place Celery worker + Beat pour tâches planifiées (backup notes hebdo, rappel quotidien).

Une fois ces huit étapes franchies, votre assistant IA saura :

* **Dialoguer** naturellement sur Telegram.
* **Envoyer** et **recevoir** des e-mails au nom de votre compte.
* **Créer** ou **mettre à jour** des événements dans votre calendrier.
* **Prendre des notes** via texte ou messages vocaux, les indexer et les restituer.
* **Chercher** pour vous des informations sur le Web et les résumer.

