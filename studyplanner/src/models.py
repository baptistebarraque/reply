from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class StudySession:
    start_time: datetime
    end_time: datetime
    subject: str
    completed: bool = False
    notes: str = ""
    productivity_rating: Optional[int] = None  # 1-10

@dataclass
class Task:
    subject: str
    deadline: datetime
    difficulty: int  # 1-5
    estimated_hours: float
    priority: TaskPriority
    description: str = ""
    completed_hours: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    sessions: List[StudySession] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convertit la tâche en dictionnaire pour l'IA"""
        return {
            "subject": self.subject,
            "days_until_deadline": (self.deadline - datetime.now()).days,
            "difficulty": self.difficulty,
            "estimated_hours": self.estimated_hours,
            "priority": self.priority.name,
            "completion_rate": self.calculate_completion_rate(),
            "remaining_hours": self.estimated_hours - self.completed_hours
        }
    
    def calculate_completion_rate(self) -> float:
        return (self.completed_hours / self.estimated_hours * 100) if self.estimated_hours > 0 else 0
    
    def add_session(self, session: StudySession) -> None:
        self.sessions.append(session)
        if session.completed:
            duration = (session.end_time - session.start_time).total_seconds() / 3600
            self.completed_hours += duration
            if self.completed_hours >= self.estimated_hours:
                self.status = TaskStatus.COMPLETED
            elif self.status == TaskStatus.PENDING:
                self.status = TaskStatus.IN_PROGRESS

    def get_recent_sessions(self, limit: int = 5) -> List[StudySession]:
        return sorted(self.sessions, key=lambda x: x.start_time, reverse=True)[:limit]

@dataclass
class StudyBlock:
    start_time: datetime
    end_time: datetime
    subject: str
    task_type: str  # 'study', 'break', 'review'
    description: Optional[str] = None
    
    @property
    def duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)

@dataclass
class DailySchedule:
    date: datetime
    blocks: List[StudyBlock] = field(default_factory=list)
    
    def add_block(self, block: StudyBlock) -> None:
        self.blocks.append(block)
        # Trier les blocs par heure de début
        self.blocks.sort(key=lambda x: x.start_time)
    
    def get_study_time(self) -> int:
        """Retourne le temps total d'étude en minutes"""
        return sum(
            block.duration_minutes 
            for block in self.blocks 
            if block.task_type == 'study'
        )
    
    def get_break_time(self) -> int:
        """Retourne le temps total de pause en minutes"""
        return sum(
            block.duration_minutes 
            for block in self.blocks 
            if block.task_type == 'break'
        )

@dataclass
class StudyStats:
    total_study_time: float  # en heures
    completed_tasks: int
    pending_tasks: int
    average_productivity: float  # 1-10
    most_studied_subject: str
    study_streak: int  # jours consécutifs
    weekly_goal_progress: float  # pourcentage
    
    def to_dict(self) -> Dict:
        return {
            "total_study_time": round(self.total_study_time, 1),
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "average_productivity": round(self.average_productivity, 1),
            "most_studied_subject": self.most_studied_subject,
            "study_streak": self.study_streak,
            "weekly_goal_progress": round(self.weekly_goal_progress, 1)
        }