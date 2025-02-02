"""
Модуль для управления хранилищем резервных копий
"""
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .backup_engine import BackupEngine

class StoragePolicy:
    def __init__(
        self,
        max_size_gb: Optional[float] = None,
        max_backups: Optional[int] = None,
        retention_days: Optional[int] = None,
        min_free_space_gb: Optional[float] = None
    ):
        self.max_size_gb = max_size_gb
        self.max_backups = max_backups
        self.retention_days = retention_days
        self.min_free_space_gb = min_free_space_gb
        
    def to_dict(self) -> Dict:
        """Конвертирует политику в словарь"""
        return {
            "max_size_gb": self.max_size_gb,
            "max_backups": self.max_backups,
            "retention_days": self.retention_days,
            "min_free_space_gb": self.min_free_space_gb
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'StoragePolicy':
        """Создает политику из словаря"""
        return cls(
            max_size_gb=data.get("max_size_gb"),
            max_backups=data.get("max_backups"),
            retention_days=data.get("retention_days"),
            min_free_space_gb=data.get("min_free_space_gb")
        )

class StorageManager:
    def __init__(self, backup_dir: str, config_file: str = "storage_config.json"):
        self.backup_dir = Path(backup_dir)
        self.config_file = Path(config_file)
        self.policy = StoragePolicy()
        self._load_config()
        
    def _load_config(self):
        """Загружает конфигурацию хранилища"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.policy = StoragePolicy.from_dict(data)
                
    def _save_config(self):
        """Сохраняет конфигурацию хранилища"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.policy.to_dict(), f, ensure_ascii=False, indent=2)
            
    def set_policy(self, policy: StoragePolicy):
        """Устанавливает политику хранения"""
        self.policy = policy
        self._save_config()
        
    def get_storage_info(self) -> Dict:
        """Возвращает информацию о хранилище"""
        total_size = 0
        backup_count = 0
        oldest_backup = None
        newest_backup = None
        
        engine = BackupEngine(self.backup_dir)
        backups = engine.list_backups()
        
        if backups:
            for backup in backups:
                total_size += backup['backup_size']
                backup_count += 1
                
                backup_date = datetime.fromisoformat(backup['backup_date'])
                if oldest_backup is None or backup_date < oldest_backup:
                    oldest_backup = backup_date
                if newest_backup is None or backup_date > newest_backup:
                    newest_backup = backup_date
                    
        # Получаем информацию о диске
        total_space = shutil.disk_usage(self.backup_dir).total
        free_space = shutil.disk_usage(self.backup_dir).free
        
        return {
            "total_size_gb": total_size / (1024 ** 3),
            "backup_count": backup_count,
            "oldest_backup": oldest_backup.isoformat() if oldest_backup else None,
            "newest_backup": newest_backup.isoformat() if newest_backup else None,
            "total_space_gb": total_space / (1024 ** 3),
            "free_space_gb": free_space / (1024 ** 3)
        }
        
    def cleanup(self) -> List[str]:
        """
        Очищает хранилище в соответствии с политикой
        
        Returns:
            List[str]: Список удаленных файлов
        """
        engine = BackupEngine(self.backup_dir)
        backups = engine.list_backups()
        deleted_files = []
        
        # Сортируем резервные копии по дате
        backups.sort(key=lambda x: datetime.fromisoformat(x['backup_date']))
        
        # Проверяем политики и удаляем лишние копии
        if self.policy.retention_days:
            cutoff_date = datetime.now() - timedelta(days=self.policy.retention_days)
            while backups and datetime.fromisoformat(backups[0]['backup_date']) < cutoff_date:
                backup = backups.pop(0)
                backup_path = self.backup_dir / backup['backup_file']
                backup_path.unlink()
                deleted_files.append(str(backup_path))
                
        if self.policy.max_backups:
            while len(backups) > self.policy.max_backups:
                backup = backups.pop(0)
                backup_path = self.backup_dir / backup['backup_file']
                backup_path.unlink()
                deleted_files.append(str(backup_path))
                
        if self.policy.max_size_gb:
            total_size = sum(b['backup_size'] for b in backups)
            max_size_bytes = self.policy.max_size_gb * (1024 ** 3)
            
            while backups and total_size > max_size_bytes:
                backup = backups.pop(0)
                backup_path = self.backup_dir / backup['backup_file']
                total_size -= backup['backup_size']
                backup_path.unlink()
                deleted_files.append(str(backup_path))
                
        if self.policy.min_free_space_gb:
            min_free_space_bytes = self.policy.min_free_space_gb * (1024 ** 3)
            while backups and shutil.disk_usage(self.backup_dir).free < min_free_space_bytes:
                backup = backups.pop(0)
                backup_path = self.backup_dir / backup['backup_file']
                backup_path.unlink()
                deleted_files.append(str(backup_path))
                
        return deleted_files
        
    def check_storage_policy(self) -> Dict[str, bool]:
        """
        Проверяет соответствие хранилища политикам
        
        Returns:
            Dict[str, bool]: Результаты проверок
        """
        info = self.get_storage_info()
        results = {}
        
        if self.policy.max_size_gb:
            results["size"] = info["total_size_gb"] <= self.policy.max_size_gb
            
        if self.policy.max_backups:
            results["backups"] = info["backup_count"] <= self.policy.max_backups
            
        if self.policy.retention_days:
            if info["oldest_backup"]:
                oldest = datetime.fromisoformat(info["oldest_backup"])
                max_age = datetime.now() - timedelta(days=self.policy.retention_days)
                results["retention"] = oldest >= max_age
            else:
                results["retention"] = True
                
        if self.policy.min_free_space_gb:
            results["free_space"] = info["free_space_gb"] >= self.policy.min_free_space_gb
            
        return results 