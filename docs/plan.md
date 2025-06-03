# Plan de Conception de l'Assistant IA

## 1. Vue d'ensemble du projet

### 1.1 Objectif
Créer un assistant IA personnel accessible via Telegram, capable de gérer emails, agenda, notes, recherche web et transcription vocale.

**KPI principal**: Temps moyen gagné par l'utilisateur ou taux d'usage quotidien une fois en production.

### 1.2 Fonctionnalités principales
- Communication naturelle via Telegram
- Envoi et réception d'emails
- Gestion d'événements de calendrier
- Prise de notes (texte et vocale)
- Recherche web et résumé d'informations
- Transcription de messages vocaux

### 1.3 Utilisateurs cibles
- Particuliers "power users" cherchant un assistant personnel numérique
- Cadres dirigeants avec besoin d'automatisation administrative
- Équipes projet nécessitant une coordination simplifiée
- Professionnels avec différents niveaux techniques, attentes de SLA et contraintes de conformité

## 2. Architecture détaillée

### 2.1 Schéma global
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Interface   │     │ Backend      │     │ Services    │
│ Telegram Bot│────▶│ FastAPI      │────▶│ Externes    │
└─────────────┘     │ + LangChain  │     └─────────────┘
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Stockage     │
                    │ PostgreSQL   │
                    │ Redis        │
                    │ Fichiers MD  │
                    └──────────────┘
```

### 2.2 Couches fonctionnelles
1. **Interface utilisateur**: Bot Telegram (aiogram 3)
2. **Logique métier**: FastAPI + LangChain Agent
3. **Services externes**: OpenAI, Gmail, Google Calendar, SerpAPI
4. **Outils spécialisés**: EmailTool, CalendarTool, SearchTool, NotesTool, VoiceTool
5. **Stockage**: PostgreSQL (métadonnées) + Fichiers Markdown (contenu)
6. **Traitement asynchrone**: Celery + Redis

### 2.3 Résilience et scalabilité
1. **Tolérance aux pannes**
   - Fallback LLM (GPT-3.5, Llama 3 local) si GPT-4o est indisponible
   - Dégradation gracieuse des fonctionnalités pour maintenir le service minimal

2. **Scalabilité horizontale**
   - Load-balancer (Fly.io regions ou Cloudflare Tunnel) pour répartir la charge
   - Politique de scaling automatique des workers Celery selon la longueur de file

3. **Observabilité**
   - Prometheus + Grafana ou flyctl dashboards pour métriques (CPU, latence, file Celery)
   - Centralisation des logs JSON (Better Stack ou Grafana Loki)

4. **Sécurité réseau**
   - Accès limité aux services internes (Redis, Postgres) via réseau privé Fly VPC
   - mTLS ou mot de passe fort pour Redis, même sans exposition publique

## 3. Structure du projet

```
assistant-IA/
├── docs/                      # Documentation
│   ├── projet.md
│   ├── plan.md
│   └── adr/                   # Architecture Decision Records
├── app/                       # Code source principal
│   ├── main.py                # Point d'entrée FastAPI
│   ├── config.py              # Configuration et variables d'environnement
│   ├── bot/                   # Logique du bot Telegram
│   │   ├── __init__.py
│   │   ├── router.py          # Routage des messages Telegram
│   │   ├── handlers/          # Gestionnaires de messages
│   │   │   ├── __init__.py
│   │   │   ├── message.py     # Messages texte
│   │   │   ├── voice.py       # Messages vocaux
│   │   │   └── callback.py    # Boutons inline
│   │   └── middleware.py      # Middlewares Telegram
│   ├── agent/                 # Logique de l'agent IA
│   │   ├── __init__.py
│   │   ├── agent.py           # Agent LangChain
│   │   └── memory.py          # Gestion de la mémoire conversationnelle
│   ├── tools/                 # Outils spécialisés
│   │   ├── __init__.py
│   │   ├── email_tool.py      # Gestion des emails
│   │   ├── calendar_tool.py   # Gestion du calendrier
│   │   ├── search_tool.py     # Recherche web
│   │   ├── notes_tool.py      # Prise de notes
│   │   └── voice_tool.py      # Transcription vocale
│   ├── models/                # Modèles de données
│   │   ├── __init__.py
│   │   ├── user.py            # Modèle utilisateur
│   │   └── note.py            # Modèle note
│   ├── services/              # Services externes
│   │   ├── __init__.py
│   │   ├── openai.py          # Client OpenAI
│   │   ├── google_auth.py     # Authentification Google
│   │   ├── gmail.py           # API Gmail
│   │   └── calendar.py        # API Calendar
│   ├── database/              # Gestion de la base de données
│   │   ├── __init__.py
│   │   ├── engine.py          # Connexion à la BDD
│   │   └── migrations/        # Migrations Alembic
│   └── tasks/                 # Tâches asynchrones
│       ├── __init__.py
│       ├── celery.py          # Configuration Celery
│       ├── router.py          # Routeur de tâches (high/default/low)
│       ├── email_tasks.py     # Tâches liées aux emails
│       └── voice_tasks.py     # Tâches de transcription
├── tests/                     # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_bot.py
│   └── test_tools.py
├── .github/workflows/         # CI/CD pipelines
├── .env.example               # Exemple de variables d'environnement
├── requirements.txt           # Dépendances Python
├── Dockerfile                 # Configuration Docker
├── docker-compose.yml         # Configuration Docker Compose
├── Procfile                   # Configuration pour déploiement cloud
└── README.md                  # Documentation principale
```

## 4. Technologies et dépendances

### 4.1 Backend et API
- **FastAPI**: Framework API moderne et performant
- **Uvicorn**: Serveur ASGI pour FastAPI
- **Pydantic**: Validation des données

### 4.2 Bot Telegram
- **aiogram 3**: Framework asynchrone pour Telegram Bot API

### 4.3 Intelligence artificielle
- **LangChain**: Orchestration d'agents IA
- **OpenAI**: Modèles GPT-4o pour le raisonnement
- **Llama 3 (via Ollama)**: Fallback LLM en cas d'indisponibilité d'OpenAI

### 4.4 Outils et intégrations
- **faster-whisper**: Transcription vocale locale
- **google-api-python-client**: Intégration Gmail et Calendar
- **google-auth-oauthlib**: Authentification OAuth Google (flux off-line avec refresh token)
- **SerpAPI/DuckDuckGo**: Recherche web

### 4.5 Stockage et base de données
- **SQLModel**: ORM combinant SQLAlchemy et Pydantic
- **PostgreSQL**: Base de données relationnelle
- **Alembic**: Migrations de base de données
- **S3-compatible**: Backend objet (Cloudflare R2, Scaleway) pour stockage des notes
- **FAISS/PGVector**: Indexation vectorielle pour recherche sémantique (RAG)

### 4.6 Traitement asynchrone
- **Celery**: Exécution de tâches asynchrones
- **Redis**: Broker de messages et stockage cache

### 4.7 Observabilité
- **Prometheus + Grafana**: Monitoring et tableaux de bord
- **Loki/Better Stack**: Agrégation de logs centralisés

### 4.8 Déploiement
- **Docker**: Conteneurisation
- **Fly.io/Railway**: Hébergement cloud
- **GitHub Actions**: CI/CD

## 5. Étapes de développement

### 5.1 Phase 1: Configuration initiale
1. Création de l'environnement virtuel et installation des dépendances
2. Configuration des variables d'environnement
3. Création du bot Telegram via BotFather
4. Configuration des API Google (Gmail, Calendar)
5. Mise en place de la structure de projet
6. Configuration CI/CD (GitHub Actions): lint, tests, build Docker

### 5.2 Phase 2: Développement du bot Telegram
1. Implémentation des handlers de messages texte
2. Implémentation des handlers de messages vocaux
3. Intégration des boutons inline et callbacks
4. Configuration du webhook FastAPI

### 5.3 Phase 3: Intégration de l'agent LangChain (MVP utilisable)
1. Configuration de l'API OpenAI
2. Mise en place de l'agent LangChain
3. Création de la mémoire conversationnelle
4. Tests de dialogue avec l'agent
5. Intégration de l'outil de recherche web
6. Déploiement sur environnement staging pour validation UX

### 5.4 Phase 4: Développement des outils
1. Implémentation de l'outil Email (Gmail API)
2. Implémentation de l'outil Calendrier (Google Calendar API)
3. Implémentation de l'outil Notes (PostgreSQL + Markdown)
4. Implémentation de l'outil Transcription vocale (faster-whisper)

### 5.5 Phase 5: Mise en place du stockage
1. Configuration de PostgreSQL
2. Création des modèles SQLModel
3. Configuration des migrations Alembic
4. Implémentation du stockage S3-compatible (notes, audio)

### 5.6 Phase 6: Traitement asynchrone
1. Configuration de Celery et Redis
2. Implémentation des tâches de transcription vocale
3. Implémentation des tâches d'envoi d'emails
4. Planification des tâches périodiques
5. Configuration des files prioritaires (high, default, low)

### 5.7 Phase 7: Tests et déploiement
1. Écriture des tests unitaires et d'intégration
2. Configuration Docker et docker-compose
3. Déploiement sur environnement de test (local)
4. Déploiement sur environnement de production (Fly.io/Railway)
5. Configuration du plan de rollback et déploiement Canary

## 6. Configuration et déploiement

### 6.1 Variables d'environnement
```
# Bot Telegram
BOT_TOKEN=

# OpenAI
OPENAI_API_KEY=

# Google API
GMAIL_CLIENT_SECRET_FILE=credentials.json
GOOGLE_PROJECT=

# Recherche Web
SERPAPI_KEY=

# Base de données
DATABASE_URL=postgresql://user:password@localhost/assistant_ia

# Redis
REDIS_URL=redis://localhost:6379/0

# Stockage Objet
S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=

# Observabilité
PROMETHEUS_ENDPOINT=
LOKI_URL=

# Déploiement
WEB_URL=https://votre-domaine.fly.dev
```

### 6.2 Conteneurisation
1. Dockerfile pour l'application principale
2. Dockerfile pour le worker Celery
3. docker-compose.yml pour développement local

### 6.3 Déploiement cloud
1. Configuration Fly.io ou Railway
2. Mise en place du volume PostgreSQL
3. Configuration du Redis addon
4. Déploiement des conteneurs Docker
5. Configuration du réseau privé VPC

## 7. Sécurité et gestion des données

### 7.1 Authentification et autorisation
1. Gestion sécurisée des tokens OAuth Google
2. Chiffrement AES-256 des tokens en base de données
3. Système d'autorisation par utilisateur Telegram
4. Rotation automatique des tokens OAuth, clés API et notification d'expiration

### 7.2 Protection des données
1. Conformité RGPD (droit à l'oubli, export de données)
2. Chiffrement des données sensibles
3. Backup automatique des notes et configuration
4. Politique de conservation des fichiers audio (purge après transcription)

### 7.3 Limitation de privilèges
1. Rôle Postgres avec privilèges minimaux pour l'application
2. Droits superuser limités aux migrations Alembic
3. Isolation des conteneurs et principe du moindre privilège

### 7.4 Monitoring et logs
1. Logging structuré avec niveaux de verbosité
2. Alertes sur erreurs critiques
3. Monitoring des quotas API (OpenAI, Google, SerpAPI)
4. Vérification automatique des certificats SSL

## 8. Extensions futures

### 8.1 Amélioration de l'IA
1. Support de LLM locaux (Llama 3 70B via Ollama)
2. Fine-tuning sur données personnelles
3. RAG (Retrieval Augmented Generation) pour documentation personnelle

### 8.2 Nouvelles fonctionnalités (par priorité)
1. Briefing quotidien (résumé mails + événements + notes)
2. Synthèse vocale (TTS) via ElevenLabs ou OpenAI TTS
3. Tableau de bord web (Streamlit ou Next.js)
4. Support multi-utilisateurs
5. Intégration d'APIs additionnelles (Notion, Obsidian)

### 8.3 Infrastructure
1. Scaling horizontal pour supporter plus d'utilisateurs
2. Mise en cache intelligente des réponses fréquentes
3. Optimisation des coûts API via batching et pooling

## 9. Risques identifiés & plans d'atténuation

| Risque                                   | Impact         | Mitigation                                                       |
| ---------------------------------------- | -------------- | ---------------------------------------------------------------- |
| Surcharges API (OpenAI, SerpAPI)         | Coûts imprévus | Mettre des quotas hard dans Celery + monitoring facturation.     |
| Blocage des webhooks (certificat expiré) | Bot inopérant  | Cron de vérif SSL + alerte Telegram.                             |
| Retards transcription (audio très longs) | UX dégradée    | Partitionner audio > 45 s en plusieurs jobs + message d'attente. |
| Requêtes Gmail massives → Quotas Google  | 403 API        | Cache des brouillons côté bot, envoi différé.                    |

## 10. Synthèse des améliorations prioritaires

1. **Observabilité complète**: Métriques + logs centralisés dès la phase alpha.
2. **Fallback LLM + plan de dégradation**: Garantir un service minimal toujours disponible.
3. **Roadmap KPI-driven**: Mesurer l'efficacité (nombre de notes créées, taux d'e-mails envoyés via le bot, NPS utilisateur).
4. **Sécurité: rotation automatique et least privilege** pour Postgres et API externes.
5. **ADR + CI/CD** pour pérenniser la maintenance et faciliter les contributions futures. 