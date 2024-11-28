from datetime import datetime, timedelta
import logging
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import print as rprint

from config.config_loader import ConfigLoader
from src.models import Task, TaskPriority, TaskStatus, StudyBlock
from src.utils import (
    format_duration, 
    calculate_time_until, 
    generate_progress_bar, 
    format_priority,
    get_emoji_for_subject
)
from src.ai_planner import AIPlannerService

class StudyPlanner:
    def __init__(self):
        """Initialisation du planificateur d'études"""
        self.console = Console()
        self.config = ConfigLoader()
        self.logger = logging.getLogger(__name__)
        self.tasks = {}
        self.ai_planner = AIPlannerService(self.config)

    def run(self):
        """Point d'entrée principal de l'application"""
        self._show_welcome_message()
        
        while True:
            try:
                choice = self._show_main_menu()
                if choice == '1':
                    self._add_new_task()
                elif choice == '2':
                    self._view_tasks()
                elif choice == '3':
                    self._update_task_progress()
                elif choice == '4':
                    self._show_daily_schedule()
                elif choice == '5':
                    self._show_weekly_schedule()
                elif choice == '6':
                    self._view_statistics()
                elif choice == '7':
                    self._manage_preferences()
                elif choice == 'q':
                    self._quit_application()
                    break
                else:
                    self.console.print("[red]Option invalide. Veuillez réessayer.[/red]")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'exécution: {e}")
                self.console.print(f"[red]Une erreur est survenue: {e}[/red]")

    def _show_welcome_message(self):
        """Affiche le message de bienvenue"""
        self.console.print("\n[bold blue]📚 Bienvenue dans votre Planificateur d'Études ![/bold blue]")

    def _show_main_menu(self) -> str:
        """Affiche le menu principal et retourne le choix de l'utilisateur"""
        options = [
            "1. Ajouter une nouvelle tâche",
            "2. Voir les tâches",
            "3. Mettre à jour la progression",
            "4. Voir le planning du jour",
            "5. Voir le planning de la semaine",
            "6. Voir les statistiques",
            "7. Gérer les préférences",
            "q. Quitter"
        ]
        
        self.console.print("\n[bold cyan]Menu Principal[/bold cyan]")
        for option in options:
            self.console.print(option)
            
        return Prompt.ask("\nVotre choix", default="1")

    def _add_new_task(self):
        """Ajoute une nouvelle tâche"""
        self.console.print("\n[bold green]Ajout d'une nouvelle tâche[/bold green]")
        
        try:
            # Collecte des informations
            subject = Prompt.ask("Matière")
            description = Prompt.ask("Description")
            
            # Date limite
            while True:
                try:
                    days = int(Prompt.ask("Nombre de jours jusqu'à la deadline"))
                    deadline = datetime.now() + timedelta(days=days)
                    break
                except ValueError:
                    self.console.print("[red]Veuillez entrer un nombre valide.[/red]")
            
            # Difficulté
            while True:
                try:
                    difficulty = int(Prompt.ask("Difficulté (1-5)"))
                    if 1 <= difficulty <= 5:
                        break
                    self.console.print("[red]La difficulté doit être entre 1 et 5.[/red]")
                except ValueError:
                    self.console.print("[red]Veuillez entrer un nombre valide.[/red]")
            
            # Temps estimé
            while True:
                try:
                    hours = float(Prompt.ask("Temps estimé (en heures)"))
                    if hours > 0:
                        break
                    self.console.print("[red]Le temps doit être positif.[/red]")
                except ValueError:
                    self.console.print("[red]Veuillez entrer un nombre valide.[/red]")
            
            # Priorité
            self.console.print("\nPriorités disponibles:")
            for priority in TaskPriority:
                self.console.print(f"{priority.value}. {priority.name}")
            
            while True:
                try:
                    priority_value = int(Prompt.ask("Priorité (1-4)"))
                    priority = list(TaskPriority)[priority_value-1]
                    break
                except (ValueError, IndexError):
                    self.console.print("[red]Priorité invalide.[/red]")
            
            # Création de la tâche
            new_task = Task(
                subject=subject,
                description=description,
                deadline=deadline,
                difficulty=difficulty,
                estimated_hours=hours,
                priority=priority
            )
            
            # Ajout de la tâche
            task_id = f"{subject.lower().replace(' ', '_')}_{len(self.tasks)}"
            self.tasks[task_id] = new_task
            self.console.print("[green]✓ Tâche ajoutée avec succès ![/green]")
            
            # Réorganisation du planning avec l'IA
            self._update_schedule_with_ai(new_task)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de la tâche: {e}")
            self.console.print(f"[red]Erreur : {e}[/red]")

    def _view_tasks(self):
        """Affiche la liste des tâches"""
        if not self.tasks:
            self.console.print("[yellow]Aucune tâche enregistrée.[/yellow]")
            return

        table = Table(title="Liste des Tâches")
        
        # Définition des colonnes
        table.add_column("Matière", style="cyan")
        table.add_column("Progression", style="green")
        table.add_column("Priorité", style="magenta")
        table.add_column("Deadline", style="yellow")
        table.add_column("Status", style="blue")
        
        # Ajout des tâches
        for task in self.tasks.values():
            emoji = get_emoji_for_subject(task.subject)
            progress = generate_progress_bar(task.calculate_completion_rate())
            time_left = calculate_time_until(task.deadline)
            
            table.add_row(
                f"{emoji} {task.subject}",
                progress,
                format_priority(task.priority.value),
                f"Dans {time_left}",
                task.status.name
            )
        
        self.console.print(table)

    def _update_task_progress(self):
        """Met à jour la progression d'une tâche"""
        if not self.tasks:
            self.console.print("[yellow]Aucune tâche à mettre à jour.[/yellow]")
            return

        # Affichage des tâches disponibles
        self.console.print("\n[bold]Tâches disponibles :[/bold]")
        for task_id, task in self.tasks.items():
            if task.status != TaskStatus.COMPLETED:
                self.console.print(f"{task_id}: {task.subject}")

        # Sélection de la tâche
        task_id = Prompt.ask("\nID de la tâche à mettre à jour")
        if task_id not in self.tasks:
            self.console.print("[red]Tâche non trouvée.[/red]")
            return

        task = self.tasks[task_id]
        if task.status == TaskStatus.COMPLETED:
            self.console.print("[yellow]Cette tâche est déjà complétée.[/yellow]")
            return

        # Mise à jour de la progression
        try:
            hours = float(Prompt.ask("Heures travaillées"))
            notes = Prompt.ask("Notes (optionnel)")

            task.completed_hours += hours
            if task.completed_hours >= task.estimated_hours:
                task.status = TaskStatus.COMPLETED
            elif task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS

            self.console.print("[green]✓ Progression mise à jour ![/green]")
            
            # Affichage de la progression
            completion_rate = task.calculate_completion_rate()
            self.console.print(f"\nProgression : {generate_progress_bar(completion_rate)}")

        except ValueError:
            self.console.print("[red]Veuillez entrer un nombre valide d'heures.[/red]")

    def _show_daily_schedule(self):
        """Affiche le planning du jour"""
        if not self.tasks:
            self.console.print("[yellow]Aucune tâche à planifier.[/yellow]")
            return

        # On prend la première tâche non complétée comme référence
        reference_task = None
        for task in self.tasks.values():
            if task.status != TaskStatus.COMPLETED:
                reference_task = task
                break

        if not reference_task:
            self.console.print("[yellow]Toutes les tâches sont complétées ![/yellow]")
            return

        schedule = self.ai_planner.generate_schedule(self.tasks, reference_task)
        if not schedule:
            self.console.print("[red]Impossible de générer le planning.[/red]")
            return

        table = Table(title=f"Planning du {datetime.now().strftime('%d/%m/%Y')}")
        table.add_column("Horaire", style="cyan")
        table.add_column("Tâche", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Commentaire", style="magenta")

        for block in schedule:
            time_slot = f"{block.start_time.strftime('%H:%M')} - {block.end_time.strftime('%H:%M')}"
            task_type = "🎯 Étude" if block.task_type == "study" else "☕️ Pause"
            
            table.add_row(
                time_slot,
                block.subject,
                task_type,
                block.description or ""
            )

        self.console.print(table)

    def _show_weekly_schedule(self):
        """Affiche le planning de la semaine"""
        if not self.tasks:
            self.console.print("[yellow]Aucune tâche à planifier.[/yellow]")
            return

        weekly_schedule = self.ai_planner.generate_weekly_schedule(self.tasks)
        if not weekly_schedule:
            self.console.print("[red]Impossible de générer le planning hebdomadaire.[/red]")
            return

        for day, schedule in weekly_schedule.items():
            table = Table(title=f"\n[bold blue]Planning - {day}[/bold blue]")
            table.add_column("Horaire", style="cyan")
            table.add_column("Tâche", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Commentaire", style="magenta")

            for block in schedule:
                time_slot = f"{block.start_time.strftime('%H:%M')} - {block.end_time.strftime('%H:%M')}"
                task_type = "🎯 Étude" if block.task_type == "study" else "☕️ Pause"
                
                table.add_row(
                    time_slot,
                    block.subject,
                    task_type,
                    block.description or ""
                )

            self.console.print(table)

    def _view_statistics(self):
        """Affiche les statistiques d'étude"""
        if not self.tasks:
            self.console.print("[yellow]Pas encore de données disponibles.[/yellow]")
            return

        table = Table(title="Statistiques d'Étude")
        table.add_column("Métrique", style="cyan")
        table.add_column("Valeur", style="green")

        # Calcul des statistiques
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() 
                             if t.status == TaskStatus.COMPLETED])
        in_progress = len([t for t in self.tasks.values() 
                          if t.status == TaskStatus.IN_PROGRESS])
        total_hours = sum(t.completed_hours for t in self.tasks.values())

        # Ajout des lignes
        table.add_row("Total des tâches", str(total_tasks))
        table.add_row("Tâches complétées", str(completed_tasks))
        table.add_row("Tâches en cours", str(in_progress))
        table.add_row("Heures totales d'étude", f"{total_hours:.1f}h")
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            table.add_row(
                "Taux de complétion",
                generate_progress_bar(completion_rate)
            )

        self.console.print(table)

    def _manage_preferences(self):
        """Gère les préférences utilisateur"""
        self.console.print("\n[bold]Gestion des Préférences[/bold]")
        
        while True:
            self.console.print("\n1. Voir les horaires actuels")
            self.console.print("2. Modifier les horaires")
            self.console.print("3. Retour au menu principal")
            
            choice = Prompt.ask("Choix", default="1")
            
            if choice == "1":
                self._show_current_schedule()
            elif choice == "2":
                self._modify_schedule()
            elif choice == "3":
                break
            else:
                self.console.print("[red]Option invalide.[/red]")

    def _show_current_schedule(self):
        """Affiche les horaires actuels"""
        current_hours = self.config.get_study_hours()
        
        table = Table(title="Horaires d'Étude")
        table.add_column("Jour", style="cyan")
        table.add_column("Créneaux", style="green")
        
        for day, slots in current_hours.items():
            table.add_row(day, ", ".join(slots))
        
        self.console.print(table)

    def _modify_schedule(self):
        """Modifie les horaires d'étude"""
        self.console.print("\nFormat: HH:MM-HH:MM (ex: 09:00-12:00)")
        self.console.print("Pour plusieurs créneaux, séparez par des virgules")
        
        new_hours = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for day in days:
            slots = Prompt.ask(f"{day}")
            if slots.strip():
                new_hours[day] = [s.strip() for s in slots.split(",")]
        
        if self.config.save_user_preferences(new_hours):
            self.console.print("[green]✓ Préférences sauvegardées ![/green]")
        else:
            self.console.print("[red]Erreur lors de la sauvegarde.[/red]")

    def _update_schedule_with_ai(self, new_task: Task):
        """Met à jour le planning avec l'IA après l'ajout d'une tâche"""
        self.console.print("\n[bold cyan]Mise à jour du planning...[/bold cyan]")
        
        new_schedule = self.ai_planner.generate_schedule(self.tasks, new_task)
        if new_schedule:
            self.console.print("\n📅 [bold green]Planning réorganisé pour aujourd'hui:[/bold green]")
            
            table = Table()
            table.add_column("Horaire", style="cyan")
            table.add_column("Tâche", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Raison", style="magenta")
            
            for block in new_schedule:
                time_slot = f"{block.start_time.strftime('%H:%M')} - {block.end_time.strftime('%H:%M')}"
                task_type = "🎯 Étude" if block.task_type == "study" else "☕️ Pause"
                
                table.add_row(
                    time_slot,
                    block.subject,
                    task_type,
                    block.description or ""
                )
            
            self.console.print(table)
        else:
            self.console.print("[yellow]Impossible de réorganiser le planning automatiquement.[/yellow]")

    def _quit_application(self):
        """Quitte l'application proprement"""
        self.console.print("\n[bold blue]Merci d'avoir utilisé le Planificateur d'Études ![/bold blue]")
        self.console.print("[italic]À bientôt ![/italic]")

if __name__ == "__main__":
    planner = StudyPlanner()
    planner.run()