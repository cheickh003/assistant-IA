# Guide de déploiement sur serveur Debian

Ce guide vous explique comment déployer l'Assistant IA sur votre serveur Debian privé.

## Prérequis

- Un serveur Debian 10 ou supérieur
- Accès SSH à votre serveur
- Accès root ou sudo

## Nouvelles fonctionnalités

Cette version de l'Assistant IA inclut deux nouvelles fonctionnalités majeures :

1. **Mémoire persistante** : Toutes les conversations et interactions sont stockées dans une base de données PostgreSQL.
2. **Support des messages vocaux** : Le bot peut maintenant transcrire et répondre à des messages vocaux envoyés via Telegram.

## Étapes de déploiement

### 1. Cloner le dépôt sur votre serveur

```bash
git clone <votre-repo> assistant-ia
cd assistant-ia
```

### 2. Configurer les variables d'environnement

```bash
cp env.template local.env
nano local.env
```

Remplissez toutes les variables requises :
- `BOT_TOKEN` : Token de votre bot Telegram
- `OPENAI_API_KEY` : Votre clé API OpenAI
- `GMAIL_CLIENT_SECRET_FILE` : Chemin vers votre fichier de credentials Google
- `GOOGLE_PROJECT` : ID de votre projet Google Cloud
- `SERPAPI_KEY` : Votre clé API SerpApi
- `WEB_URL` : URL publique de votre serveur (pour les webhooks)
- `DATABASE_URL` : URL de connexion à la base de données PostgreSQL (prédéfinie dans docker-compose)
- `REDIS_URL` : URL de connexion à Redis (prédéfinie dans docker-compose)

### 3. Utiliser le script de déploiement automatique

```bash
chmod +x deploy.sh
./deploy.sh
```

Ce script va :
- Installer Docker et Docker Compose s'ils ne sont pas présents
- Vérifier la présence du fichier local.env
- Construire et démarrer les conteneurs

### 4. Déploiement manuel

Si vous préférez le déploiement manuel, suivez ces étapes :

```bash
# Installation de Docker
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Installation de Docker Compose
sudo apt install -y docker-compose-plugin

# Déploiement du conteneur
docker-compose up -d --build
```

## Configuration du webhook Telegram

Pour que Telegram puisse communiquer avec votre bot, assurez-vous que :

1. Votre serveur est accessible depuis Internet
2. Vous avez configuré correctement la variable `WEB_URL` dans local.env
3. Si vous utilisez un pare-feu, ouvrez le port 8080

## Gestion des données persistantes

### Accès à l'historique des conversations

L'API expose un endpoint pour accéder à l'historique des conversations d'un utilisateur :

```
GET /api/history/{telegram_id}
```

### Sauvegarde des données

Pour sauvegarder les données de votre base PostgreSQL :

```bash
docker-compose exec postgres pg_dump -U postgres assistant_ia > backup-$(date +%Y%m%d).sql
```

### Restauration des données

Pour restaurer une sauvegarde :

```bash
cat backup.sql | docker-compose exec -T postgres psql -U postgres assistant_ia
```

## Messages vocaux

Le bot prend maintenant en charge les messages vocaux. Lorsqu'un utilisateur envoie un message vocal :

1. Le bot télécharge le fichier audio
2. Le fichier est transcrit en texte à l'aide de Whisper
3. La transcription est traitée comme un message textuel normal
4. La réponse est envoyée à l'utilisateur

Les fichiers audio sont stockés dans un volume Docker persistant (`audio_data`).

## Maintenance

### Afficher les logs

```bash
docker-compose logs -f
```

### Redémarrer le service

```bash
docker-compose restart
```

### Mettre à jour l'application

```bash
git pull
docker-compose down
docker-compose up -d --build
```

### Arrêter le service

```bash
docker-compose down
```

### Arrêter le service en conservant les données

```bash
docker-compose down
```

### Arrêter le service et supprimer toutes les données

```bash
docker-compose down -v
``` 