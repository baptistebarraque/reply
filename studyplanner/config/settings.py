# config/settings.py

import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"

# Créer le dossier logs s'il n'existe pas
LOG_DIR.mkdir(exist_ok=True)

# Configuration OpenAI
OPENAI_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 150
}

# Configuration des horaires d'étude par défaut
DEFAULT_STUDY_HOURS = {
    "Monday": ["09:00-12:00", "14:00-17:00"],
    "Tuesday": ["09:00-12:00", "14:00-17:00"],
    "Wednesday": ["09:00-12:00", "14:00-17:00"],
    "Thursday": ["09:00-12:00", "14:00-17:00"],
    "Friday": ["09:00-12:00", "14:00-16:00"],
}

# Configuration des pauses
BREAK_CONFIG = {
    "short_break": 5,  # minutes
    "long_break": 15,  # minutes
    "study_interval": 25,  # minutes (Pomodoro style)
    "sessions_until_long_break": 4  # nombre de sessions avant une longue pause
}

# Configuration des priorités
PRIORITY_WEIGHTS = {
    "deadline": 0.4,
    "difficulty": 0.3,
    "importance": 0.3
}

# Messages personnalisés
MESSAGES = {
    "welcome": "Bienvenue dans votre planificateur d'études !",
    "task_added": "✅ Tâche ajoutée avec succès !",
    "task_updated": "📝 Progression mise à jour !",
    "session_complete": "🎉 Bravo pour cette session d'étude !",
    "break_time": "⏰ C'est l'heure de faire une pause !",
    "error": "❌ Une erreur est survenue : {}"
}

# Configuration du logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "study_planner.log"),
            "mode": "a",
        },
        "error_file": {
            "level": "ERROR",
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "mode": "a",
        }
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True
        },
        "study_planner.error": {  # Error logger
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False
        }
    }
}

# Configuration des rappels
REMINDER_CONFIG = {
    "advance_notice": 15,  # minutes avant le début d'une session
    "break_notice": 2,     # minutes avant la fin d'une pause
    "end_notice": 5        # minutes avant la fin d'une session
}

# Configuration de la difficulté
DIFFICULTY_LEVELS = {
    1: "Très facile",
    2: "Facile",
    3: "Moyen",
    4: "Difficile",
    5: "Très difficile"
}

# Temps d'étude recommandé par niveau de difficulté (en minutes)
DIFFICULTY_TIME_MAPPING = {
    1: 30,
    2: 45,
    3: 60,
    4: 90,
    5: 120
}