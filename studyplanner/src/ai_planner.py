import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import openai
from .models import Task, StudyBlock
import requests

logger = logging.getLogger(__name__)

class AIPlannerService:
    def __init__(self, config):
        self.config = config
        openai.api_key = ""

    def generate_schedule(self, tasks: Dict[str, Task], new_task: Task) -> Optional[List[StudyBlock]]:
        """Génère un planning optimisé en utilisant l'IA"""
        try:
            # Préparation des données pour l'IA
            tasks_data = [task.to_dict() for task in tasks.values()]
            new_task_data = new_task.to_dict()
            
            
                
            # Construction du prompt
            prompt = self._build_prompt(tasks_data, new_task_data)
            
            # Appel à l'API GPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un expert en planification d'études qui crée des plannings optimisés."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Traitement de la réponse
            schedule_data = json.loads(response.choices[0].message['content'])
            MAKE_WEHOOK_GET_CREATE = "https://hook.eu2.make.com/1l1mql7gmx43aev4a1spnkfit73vmlvb"
            def create_event(new_task_data):
                response = requests.post(MAKE_WEHOOK_GET_CREATE,json=new_task_data)
            create_event(schedule_data)
            return self._create_study_blocks(schedule_data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du planning: {e}")
            return None

    def _build_prompt(self, tasks_data: List[Dict], new_task_data: Dict) -> str:
        """Construit le prompt pour l'IA"""
        study_hours = self.config.get_study_hours().get(
            datetime.now().strftime("%A"), []
        )
        
        return f"""
        Analyse ces données et propose un planning optimisé:

        Nouvelle tâche:
        {json.dumps(new_task_data, indent=2)}

        Tâches existantes:
        {json.dumps(tasks_data, indent=2)}

        Créneaux disponibles aujourd'hui:
        {json.dumps(study_hours, indent=2)}

        Règles à suivre:
        1. Les tâches urgentes sont prioritaires
        2. Alterner les matières pour éviter la fatigue
        3. Inclure des pauses de 15 minutes toutes les 2 heures
        4. Tenir compte de la difficulté pour la durée des sessions

        Retourne le planning au format JSON:
        {{
            "schedule": [
                {{
                    "start_time": "HH:MM",
                    "end_time": "HH:MM",
                    "task": "nom_de_la_tache",
                    "type": "study/break",
                    "reason": "justification"
                }}
            ]
        }}
        """

    def _create_study_blocks(self, schedule_data: Dict) -> List[StudyBlock]:
        """Convertit les données du planning en StudyBlocks"""
        study_blocks = []
        
        for slot in schedule_data.get("schedule", []):
            try:
                block = StudyBlock(
                    start_time=datetime.strptime(slot["start_time"], "%H:%M").replace(
                        year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day
                    ),
                    end_time=datetime.strptime(slot["end_time"], "%H:%M").replace(
                        year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day
                    ),
                    subject=slot["task"],
                    task_type=slot["type"],
                    description=slot.get("reason", "")
                )
                study_blocks.append(block)
            except Exception as e:
                logger.error(f"Erreur lors de la création d'un block d'étude: {e}")
                continue
        
        return study_blocks

    def generate_weekly_schedule(self, tasks: Dict[str, Task]) -> Optional[Dict[str, List[StudyBlock]]]:
        """Génère un planning optimisé pour la semaine entière"""
        try:
            # Préparation des données pour l'IA
            tasks_data = [task.to_dict() for task in tasks.values()]
            study_hours = self.config.get_study_hours()
            
            prompt = f"""
            Crée un planning d'études optimisé pour la semaine complète.

            Tâches à planifier:
            {json.dumps(tasks_data, indent=2)}

            Créneaux disponibles par jour:
            {json.dumps(study_hours, indent=2)}

            Règles à suivre:
            1. Répartir les tâches de manière optimale sur la semaine
            2. Prioriser les tâches selon leurs deadlines et leur importance
            3. Alterner les matières difficiles et plus faciles
            4. Prévoir des pauses régulières
            5. Tenir compte de la charge cognitive par jour
            6. Garder du temps pour les révisions

            Retourne un planning structuré par jour au format JSON:
            {{
                "Monday": [
                    {{
                        "start_time": "HH:MM",
                        "end_time": "HH:MM",
                        "task": "nom_de_la_tache",
                        "type": "study/break",
                        "reason": "justification"
                    }}
                ],
                ...autres jours
            }}
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en planification d'études qui crée des plannings hebdomadaires optimisés."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            weekly_schedule = json.loads(response.choices[0].message['content'])
            return self._process_weekly_schedule(weekly_schedule)

        except Exception as e:
            logger.error(f"Erreur lors de la génération du planning hebdomadaire: {e}")
            return None

    def _process_weekly_schedule(self, schedule_data: Dict) -> Dict[str, List[StudyBlock]]:
        """Convertit les données du planning hebdomadaire en StudyBlocks organisés par jour"""
        weekly_blocks = {}
        current_date = datetime.now()
        
        for day_name, slots in schedule_data.items():
            day_blocks = []
            # Trouver la prochaine occurrence de ce jour
            target_date = self._get_next_day_date(current_date, day_name)
            
            for slot in slots:
                try:
                    block = StudyBlock(
                        start_time=datetime.strptime(f"{target_date.date()} {slot['start_time']}", 
                                                   "%Y-%m-%d %H:%M"),
                        end_time=datetime.strptime(f"{target_date.date()} {slot['end_time']}", 
                                                 "%Y-%m-%d %H:%M"),
                        subject=slot['task'],
                        task_type=slot['type'],
                        description=slot.get('reason', '')
                    )
                    day_blocks.append(block)
                except Exception as e:
                    logger.error(f"Erreur lors de la création d'un block pour {day_name}: {e}")
                    continue
            
            weekly_blocks[day_name] = day_blocks
        
        return weekly_blocks

    def _get_next_day_date(self, current_date: datetime, target_day: str) -> datetime:
        """Trouve la prochaine occurrence d'un jour donné"""
        days = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
            'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        current_weekday = current_date.weekday()
        target_weekday = days[target_day]
        
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
            
        return current_date + timedelta(days=days_ahead)