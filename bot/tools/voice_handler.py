import os
import time
import logging
from faster_whisper import WhisperModel
from tempfile import NamedTemporaryFile
from pathlib import Path

# Configuration des répertoires
AUDIO_DIR = Path("/app/audio_data")
if not AUDIO_DIR.exists():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Configurer le modèle Whisper
model_size = "base"  # Peut être "tiny", "base", "small", "medium", "large"
model = None  # Chargé à la demande pour économiser de la mémoire

def get_model():
    """Retourne une instance du modèle Whisper, en le chargeant si nécessaire."""
    global model
    if model is None:
        try:
            # Utilise CUDA si disponible, sinon CPU
            model = WhisperModel(model_size, device="cuda", compute_type="float16")
        except:
            # Fallback sur CPU
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return model

async def process_voice_message(bot, message):
    """Traite un message vocal, le transcrit et le renvoie au traitement normal."""
    user_id = message.from_user.id
    voice = message.voice
    
    if not voice:
        return "Ce n'est pas un message vocal valide."
    
    try:
        # Informer l'utilisateur que le traitement est en cours
        status_message = await message.reply("Je traite votre message vocal...")
        
        # Télécharger le fichier audio
        file_id = voice.file_id
        file = await bot.get_file(file_id)
        
        # Créer un nom de fichier unique basé sur l'ID utilisateur et le timestamp
        timestamp = int(time.time())
        voice_path = AUDIO_DIR / f"voice_{user_id}_{timestamp}.ogg"
        
        # Télécharger le fichier vocal
        await bot.download_file(file.file_path, voice_path)
        
        # Transcrire l'audio
        model = get_model()
        segments, info = model.transcribe(str(voice_path), language="fr")
        
        # Assembler la transcription
        transcription = " ".join([segment.text for segment in segments])
        
        # Modifier le message de statut au lieu d'en envoyer un nouveau
        await status_message.edit_text(f"Transcription: {transcription}")
        
        # Retourner la transcription pour un traitement ultérieur
        return transcription
        
    except Exception as e:
        logging.error(f"Erreur lors du traitement vocal: {str(e)}")
        await message.reply("Désolé, je n'ai pas pu traiter votre message vocal.")
        return None 