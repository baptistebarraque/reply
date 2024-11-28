from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def parse_time_slot(time_slot: str) -> tuple[datetime, datetime]:
    """Convertit un créneau horaire en objets datetime"""
    try:
        start_str, end_str = time_slot.split("-")
        today = datetime.now().date()
        
        start_time = datetime.strptime(f"{today} {start_str}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{today} {end_str}", "%Y-%m-%d %H:%M")
        
        return start_time, end_time
    except ValueError as e:
        logger.error(f"Erreur lors du parsing du créneau horaire {time_slot}: {e}")
        raise

def format_duration(minutes: int) -> str:
    """Formate une durée en minutes en texte lisible"""
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return f"{hours}h {mins}min"
    elif hours:
        return f"{hours}h"
    else:
        return f"{mins}min"

def calculate_time_until(target_time: datetime) -> str:
    """Calcule et formate le temps restant jusqu'à une date donnée"""
    now = datetime.now()
    diff = target_time - now
    
    if diff.days > 0:
        return f"{diff.days} jour{'s' if diff.days > 1 else ''}"
    
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes}min"

def save_json(data: Dict, filepath: Path) -> bool:
    """Sauvegarde des données au format JSON"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier {filepath}: {e}")
        return False

def load_json(filepath: Path) -> Optional[Dict]:
    """Charge des données depuis un fichier JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {filepath}: {e}")
        return None

def validate_time_format(time_str: str) -> bool:
    """Vérifie si une chaîne respecte le format HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def get_week_dates() -> List[datetime]:
    """Retourne les dates de la semaine en cours"""
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

def format_session_time(session_time: datetime) -> str:
    """Formate une heure de session en texte lisible"""
    return session_time.strftime("%H:%M")

def calculate_study_streak(sessions: List[datetime]) -> int:
    """Calcule le nombre de jours consécutifs d'étude"""
    if not sessions:
        return 0
        
    # Convertir les sessions en dates uniques et triées
    study_dates = sorted(set(session.date() for session in sessions), reverse=True)
    
    if not study_dates:
        return 0
        
    streak = 1
    for i in range(len(study_dates) - 1):
        if (study_dates[i] - study_dates[i + 1]).days == 1:
            streak += 1
        else:
            break
            
    return streak

def generate_progress_bar(progress: float, width: int = 20) -> str:
    """Génère une barre de progression textuelle"""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress:.1f}%"

def format_priority(priority: int) -> str:
    """Formate une priorité en texte avec emoji"""
    priority_map = {
        1: "🟢 Faible",
        2: "🟡 Moyenne",
        3: "🟠 Haute",
        4: "🔴 Urgente"
    }
    return priority_map.get(priority, "❓ Inconnue")

def get_emoji_for_subject(subject: str) -> str:
    """Retourne un emoji approprié pour une matière"""
    subject_emojis = {
        "mathématiques": "📐",
        "physique": "⚡",
        "chimie": "🧪",
        "biologie": "🧬",
        "informatique": "💻",
        "histoire": "📚",
        "géographie": "🌍",
        "langues": "💬",
        "littérature": "📖",
        "arts": "🎨"
    }
    
    # Recherche insensible à la casse
    lower_subject = subject.lower()
    for key, emoji in subject_emojis.items():
        if key in lower_subject:
            return emoji
    return "📚"  # Emoji par défaut

def format_time_range(start: datetime, end: datetime) -> str:
    """Formate une plage horaire en texte lisible"""
    return f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"