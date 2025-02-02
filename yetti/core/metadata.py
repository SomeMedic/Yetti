"""
Модуль для работы с метаданными резервных копий
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

class MetadataManager:
    @staticmethod
    def calculate_hash(file_path: Path) -> str:
        """Вычисляет SHA-256 хеш файла"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def get_file_metadata(path: Path) -> Dict:
        """Получает метаданные файла или директории"""
        stat = path.stat()
        metadata = {
            "name": path.name,
            "original_path": str(path.absolute()),
            "type": "file" if path.is_file() else "directory",
            "size": stat.st_size if path.is_file() else None,
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "backup_date": datetime.now().isoformat(),
            "permissions": str(oct(stat.st_mode)[-3:])
        }
        
        if path.is_file():
            metadata["hash"] = MetadataManager.calculate_hash(path)
            
        elif path.is_dir():
            files = {}
            total_size = 0
            for item in path.rglob("*"):
                if item.is_file():
                    files[str(item.relative_to(path))] = {
                        "size": item.stat().st_size,
                        "hash": MetadataManager.calculate_hash(item)
                    }
                    total_size += item.stat().st_size
            metadata["files"] = files
            metadata["total_size"] = total_size
            
        return metadata
    
    @staticmethod
    def save_metadata(metadata: Dict, path: Path) -> None:
        """Сохраняет метаданные в файл"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_metadata(path: Path) -> Dict:
        """Загружает метаданные из файла"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    @staticmethod
    def verify_integrity(backup_path: Path, metadata: Dict) -> bool:
        """Проверяет целостность резервной копии"""
        if metadata["type"] == "file":
            current_hash = MetadataManager.calculate_hash(backup_path)
            return current_hash == metadata["hash"]
        else:
            for file_path, file_info in metadata["files"].items():
                full_path = backup_path / file_path
                if not full_path.exists():
                    return False
                current_hash = MetadataManager.calculate_hash(full_path)
                if current_hash != file_info["hash"]:
                    return False
            return True 