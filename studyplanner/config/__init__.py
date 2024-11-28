# config/__init__.py

from .config_loader import ConfigLoader
from .settings import (
    DEFAULT_STUDY_HOURS,
    BREAK_CONFIG,
    PRIORITY_WEIGHTS,
    MESSAGES,
    DIFFICULTY_LEVELS,
    DIFFICULTY_TIME_MAPPING,
    REMINDER_CONFIG
)

__all__ = [
    'ConfigLoader',
    'DEFAULT_STUDY_HOURS',
    'BREAK_CONFIG',
    'PRIORITY_WEIGHTS',
    'MESSAGES',
    'DIFFICULTY_LEVELS',
    'DIFFICULTY_TIME_MAPPING',
    'REMINDER_CONFIG'
]