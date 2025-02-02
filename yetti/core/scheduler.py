"""
Модуль для планирования резервных копий
"""
import json
import time
import threading
import schedule
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .backup_engine import BackupEngine
from .compression import CompressionMethod

class BackupTask:
    def __init__(
        self,
        source: str,
        backup_dir: str,
        schedule_type: str,
        schedule_value: str,
        compression_method: str = "zlib",
        compression_level: int = 6,
        password: Optional[str] = None,
        task_id: Optional[str] = None
    ):
        self.source = source
        self.backup_dir = backup_dir
        self.schedule_type = schedule_type  # daily, weekly, monthly
        self.schedule_value = schedule_value  # время для daily, день недели для weekly, etc
        self.compression_method = compression_method
        self.compression_level = compression_level
        self.password = password
        self.task_id = task_id or f"task_{int(time.time())}"
        
    def to_dict(self) -> Dict:
        """Конвертирует задачу в словарь"""
        return {
            "task_id": self.task_id,
            "source": self.source,
            "backup_dir": self.backup_dir,
            "schedule_type": self.schedule_type,
            "schedule_value": self.schedule_value,
            "compression_method": self.compression_method,
            "compression_level": self.compression_level,
            "password": self.password
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'BackupTask':
        """Создает задачу из словаря"""
        return cls(
            source=data["source"],
            backup_dir=data["backup_dir"],
            schedule_type=data["schedule_type"],
            schedule_value=data["schedule_value"],
            compression_method=data.get("compression_method", "zlib"),
            compression_level=data.get("compression_level", 6),
            password=data.get("password"),
            task_id=data.get("task_id")
        )

class BackupScheduler:
    def __init__(self, config_file: str = "backup_schedule.json"):
        self.config_file = Path(config_file)
        self.tasks: Dict[str, BackupTask] = {}
        self.running = False
        self._load_tasks()
        
    def _load_tasks(self):
        """Загружает задачи из файла конфигурации"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data:
                    task = BackupTask.from_dict(task_data)
                    self.tasks[task.task_id] = task
                    
    def _save_tasks(self):
        """Сохраняет задачи в файл конфигурации"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(
                [task.to_dict() for task in self.tasks.values()],
                f,
                ensure_ascii=False,
                indent=2
            )
            
    def add_task(self, task: BackupTask) -> str:
        """Добавляет новую задачу"""
        self.tasks[task.task_id] = task
        self._save_tasks()
        if self.running:
            self._schedule_task(task)
        return task.task_id
        
    def remove_task(self, task_id: str):
        """Удаляет задачу"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            schedule.clear(task_id)
            
    def get_tasks(self) -> List[BackupTask]:
        """Возвращает список всех задач"""
        return list(self.tasks.values())
        
    def _schedule_task(self, task: BackupTask):
        """Планирует выполнение задачи"""
        def job():
            try:
                engine = BackupEngine(task.backup_dir)
                engine.create_backup(
                    task.source,
                    compression_method=CompressionMethod(task.compression_method),
                    compression_level=task.compression_level,
                    password=task.password
                )
            except Exception as e:
                print(f"Ошибка при выполнении задачи {task.task_id}: {str(e)}")
                
        if task.schedule_type == "daily":
            schedule.every().day.at(task.schedule_value).do(job).tag(task.task_id)
        elif task.schedule_type == "weekly":
            day, time = task.schedule_value.split()
            getattr(schedule.every(), day.lower()).at(time).do(job).tag(task.task_id)
        elif task.schedule_type == "monthly":
            day, time = task.schedule_value.split()
            schedule.every().month.at(f"{day} {time}").do(job).tag(task.task_id)
            
    def start(self):
        """Запускает планировщик"""
        if not self.running:
            self.running = True
            
            # Планируем все задачи
            for task in self.tasks.values():
                self._schedule_task(task)
                
            # Запускаем поток планировщика
            def run_scheduler():
                while self.running:
                    schedule.run_pending()
                    time.sleep(1)
                    
            self.scheduler_thread = threading.Thread(target=run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
    def stop(self):
        """Останавливает планировщик"""
        if self.running:
            self.running = False
            schedule.clear()
            if hasattr(self, 'scheduler_thread'):
                self.scheduler_thread.join() 