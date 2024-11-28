class StudyPlannerError(Exception):
    """Classe de base pour les exceptions du planificateur d'études"""
    pass

class ConfigurationError(StudyPlannerError):
    """Erreur liée à la configuration"""
    pass

class TaskError(StudyPlannerError):
    """Erreur liée aux tâches"""
    pass

class ScheduleError(StudyPlannerError):
    """Erreur liée à la planification"""
    pass

class ValidationError(StudyPlannerError):
    """Erreur de validation des données"""
    pass

class APIError(StudyPlannerError):
    """Erreur liée aux appels API externes"""
    pass

class TimeSlotError(StudyPlannerError):
    """Erreur liée aux créneaux horaires"""
    pass

class DataStorageError(StudyPlannerError):
    """Erreur liée au stockage des données"""
    pass

class SessionError(StudyPlannerError):
    """Erreur liée aux sessions d'étude"""
    pass

class UserPreferenceError(StudyPlannerError):
    """Erreur liée aux préférences utilisateur"""
    pass