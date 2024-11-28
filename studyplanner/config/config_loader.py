# config/config_loader.py

import os
import yaml
import logging.config
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .settings import *

class ConfigLoader:
    """Gestionnaire de configuration pour le planificateur d'études"""

    def __init__(self):
        """Initialise le gestionnaire de configuration"""
        self.logger = None
        self.user_preferences = {}
        self.load_environment()
        self.setup_logging()
        self.load_user_preferences()

    def load_environment(self) -> None:
        """Charge les variables d'environnement depuis .env"""
        env_path = BASE_DIR / '.env'
        load_dotenv(env_path)
        
        # Vérification des variables d'environnement requises
        required_vars = ['OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        

    def setup_logging(self) -> None:
        """Configure le système de logging"""
        try:
            logging.config.dictConfig(LOGGING_CONFIG)
            self.logger = logging.getLogger(__name__)
            self.logger.info("Système de logging initialisé")
        except Exception as e:
            print(f"Erreur lors de l'initialisation du logging: {e}")
            # Configuration de base en cas d'échec
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)

    def load_user_preferences(self) -> None:
        """Charge les préférences utilisateur depuis le fichier YAML"""
        self.user_preferences = DEFAULT_STUDY_HOURS.copy()
        prefs_path = CONFIG_DIR / 'preferences.yaml'
        
        if prefs_path.exists():
            try:
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    user_prefs = yaml.safe_load(f)
                if user_prefs and isinstance(user_prefs, dict):
                    # Validation des préférences utilisateur
                    validated_prefs = self._validate_preferences(user_prefs)
                    self.user_preferences.update(validated_prefs)
                    self.logger.info("Préférences utilisateur chargées avec succès")
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement des préférences: {e}")
                self.logger.info("Utilisation des préférences par défaut")
        else:
            self.logger.info("Aucun fichier de préférences trouvé, utilisation des valeurs par défaut")

    def _validate_preferences(self, prefs: Dict) -> Dict:
        """Valide les préférences utilisateur"""
        validated = {}
        for day, times in prefs.items():
            if day not in DEFAULT_STUDY_HOURS:
                self.logger.warning(f"Jour invalide ignoré: {day}")
                continue
                
            valid_times = []
            for time_slot in times:
                try:
                    start, end = time_slot.split("-")
                    # Vérification basique du format heure
                    if all(self._is_valid_time(t) for t in [start, end]):
                        valid_times.append(time_slot)
                    else:
                        self.logger.warning(f"Format d'heure invalide ignoré: {time_slot}")
                except Exception:
                    self.logger.warning(f"Format de créneau horaire invalide ignoré: {time_slot}")
            
            if valid_times:
                validated[day] = valid_times
                
        return validated

    @staticmethod
    def _is_valid_time(time_str: str) -> bool:
        """Vérifie si une chaîne représente une heure valide"""
        try:
            hours, minutes = map(int, time_str.split(":"))
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except:
            return False

    def save_user_preferences(self, preferences: Dict) -> bool:
        """Sauvegarde les préférences utilisateur"""
        try:
            validated_prefs = self._validate_preferences(preferences)
            if not validated_prefs:
                self.logger.error("Aucune préférence valide à sauvegarder")
                return False

            prefs_path = CONFIG_DIR / 'preferences.yaml'
            with open(prefs_path, 'w', encoding='utf-8') as f:
                yaml.dump(validated_prefs, f, allow_unicode=True)
            
            self.user_preferences = validated_prefs
            self.logger.info("Préférences utilisateur sauvegardées avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde des préférences: {e}")
            return False

    def get_study_hours(self) -> Dict[str, list]:
        """Retourne les horaires d'étude configurés"""
        return self.user_preferences

    def get_openai_config(self) -> Dict[str, Any]:
        """Retourne la configuration OpenAI"""
        return {
            **OPENAI_CONFIG,
            "api_key": os.getenv('OPENAI_API_KEY')
        }

    def get_break_config(self) -> Dict[str, int]:
        """Retourne la configuration des pauses"""
        return BREAK_CONFIG

    def get_priority_weights(self) -> Dict[str, float]:
        """Retourne les poids des priorités"""
        return PRIORITY_WEIGHTS

    def get_message(self, key: str, **kwargs) -> str:
        """Retourne un message personnalisé avec formatage optionnel"""
        message = MESSAGES.get(key, "")
        if kwargs:
            try:
                return message.format(**kwargs)
            except KeyError as e:
                self.logger.error(f"Erreur de formatage du message '{key}': {e}")
                return message
        return message

    def get_difficulty_info(self, level: int) -> Optional[Dict[str, Any]]:
        """Retourne les informations pour un niveau de difficulté"""
        if level in DIFFICULTY_LEVELS:
            return {
                "description": DIFFICULTY_LEVELS[level],
                "recommended_time": DIFFICULTY_TIME_MAPPING[level]
            }
        return None

    def get_reminder_config(self) -> Dict[str, int]:
        """Retourne la configuration des rappels"""
        return REMINDER_CONFIG