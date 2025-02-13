"""
Основной модуль для создания резервных копий
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Union, Dict, List, Optional
from .metadata import MetadataManager
from .compression import Compressor, CompressionMethod
from .encryption import Encryptor
import sys
from .constants import EXTENSION_YETTI, EXTENSION_ONI, SUPPORTED_EXTENSIONS

def get_default_backup_dir() -> Path:
    """
    Возвращает путь к директории для бэкапов по умолчанию
    
    Returns:
        Path: Путь к директории .yetti в домашней директории пользователя
    """
    return Path.home() / ".yetti"

class BackupEngine:
    def __init__(self, backup_dir: Optional[Union[str, Path]] = None):
        """
        Инициализация движка резервного копирования
        
        Args:
            backup_dir: Директория для хранения резервных копий. 
                       Если None, используется директория по умолчанию
        """
        self.backup_dir = Path(backup_dir) if backup_dir else get_default_backup_dir()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_manager = MetadataManager()
        
    def get_backup_by_name(self, name: str) -> Optional[Path]:
        """
        Поиск бэкапа по имени
        
        Args:
            name: Имя бэкапа (без расширения .yetti)
            
        Returns:
            Optional[Path]: Путь к файлу бэкапа или None если не найден
        """
        backup_path = self.backup_dir / f"{name}.yetti"
        return backup_path if backup_path.exists() else None
        
    def create_backup(
        self,
        source: Union[str, Path],
        compression_method: CompressionMethod = CompressionMethod.ZLIB,
        compression_level: int = 6,
        password: Optional[str] = None,
        extension: str = EXTENSION_YETTI
    ) -> Path:
        """
        Создает резервную копию файла или директории.

        Args:
            source: Путь к файлу или директории для резервного копирования
            compression_method: Метод сжатия
            compression_level: Уровень сжатия (1-9)
            password: Пароль для шифрования (если None, шифрование не используется)
            extension: Расширение файла резервной копии (.yetti или .👹)
            
        Returns:
            Path: Путь к созданному файлу резервной копии
        """
        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Неподдерживаемое расширение: {extension}. Поддерживаются: {', '.join(SUPPORTED_EXTENSIONS)}")

        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Путь не существует: {source}")
            
        print(f"Создание резервной копии: {source_path}")
        print(f"Метод сжатия: {compression_method.value}, уровень: {compression_level}")
        
        # Создаем имя файла резервной копии
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source_path.name}_{timestamp}{extension}"
        backup_path = self.backup_dir / backup_name
        
        print(f"Путь резервной копии: {backup_path}")
        
        # Создаем временные директории
        temp_dir = self.backup_dir / f"temp_{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        compressed_dir = self.backup_dir / f"compressed_{timestamp}"
        compressed_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Копируем данные
            if source_path.is_file():
                print(f"Копирование файла: {source_path}")
                shutil.copy2(source_path, temp_dir)
            else:
                print(f"Копирование директории: {source_path}")
                shutil.copytree(source_path, temp_dir / source_path.name)
                
            # Получаем и сохраняем метаданные
            print("Создание метаданных")
            metadata = self.metadata_manager.get_file_metadata(source_path)
            metadata["compression"] = {
                "method": compression_method.value,
                "level": compression_level
            }
            metadata["encrypted"] = password is not None
            
            # Сжимаем каждый файл
            print("Сжатие файлов")
            for item in temp_dir.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(temp_dir)
                    compressed_path = compressed_dir / relative_path
                    compressed_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    print(f"Сжатие файла: {item} -> {compressed_path}")
                    Compressor.compress_file(
                        item,
                        compressed_path,
                        method=compression_method,
                        level=compression_level
                    )
                    
            # Сохраняем метаданные в сжатую директорию без сжатия
            metadata_path = compressed_dir / "metadata.json"
            self.metadata_manager.save_metadata(metadata, metadata_path)
            print(f"Метаданные сохранены: {metadata}")
                    
            # Создаем архив
            print("Создание архива")
            if password:
                # Если задан пароль, шифруем архив
                archive_path = backup_path.with_suffix(".zip")
                print(f"Создание временного архива: {archive_path}")
                shutil.make_archive(str(archive_path.with_suffix("")), "zip", compressed_dir)
                print(f"Шифрование архива: {archive_path} -> {backup_path}")
                Encryptor.encrypt_file(archive_path, backup_path, password)
                archive_path.unlink()  # Удаляем незашифрованный архив
            else:
                # Иначе просто создаем архив
                print(f"Создание архива: {backup_path}")
                shutil.make_archive(str(backup_path.with_suffix("")), "zip", compressed_dir)
                os.rename(backup_path.with_suffix(".zip"), backup_path)
                
            print("Резервная копия создана успешно")
            return backup_path
            
        except Exception as e:
            print(f"Ошибка при создании резервной копии: {e}")
            # В случае ошибки удаляем созданную резервную копию
            if backup_path.exists():
                backup_path.unlink()
            raise e
            
        finally:
            # Очищаем временные файлы
            try:
                if temp_dir.exists():
                    print(f"Очистка временной директории: {temp_dir}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                if compressed_dir.exists():
                    print(f"Очистка директории сжатых файлов: {compressed_dir}")
                    shutil.rmtree(compressed_dir, ignore_errors=True)
            except Exception as e:
                print(f"Ошибка при очистке временных файлов: {e}")
                pass  # Игнорируем ошибки при очистке
                
    def restore_backup(
        self,
        backup_path: Union[str, Path],
        dest: Union[str, Path],
        password: Optional[str] = None
    ) -> Path:
        """
        Восстанавливает резервную копию
        
        Args:
            backup_path: Путь к файлу резервной копии
            dest: Путь для восстановления
            password: Пароль для расшифровки (если требуется)
            
        Returns:
            Path: Путь к восстановленным данным
        """
        backup_path = Path(backup_path)
        dest_path = Path(dest)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Файл резервной копии не найден: {backup_path}")
            
        print(f"Восстановление из: {backup_path}")
        print(f"Путь назначения: {dest_path}")
        
        # Создаем временные директории
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = self.backup_dir / f"restore_{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Расшифровываем архив если нужно
            if password:
                print("Расшифровка архива...")
                encrypted_path = backup_path
                decrypted_path = temp_dir / "decrypted.zip"
                Encryptor.decrypt_file(encrypted_path, decrypted_path, password)
                archive_path = decrypted_path
            else:
                archive_path = backup_path
                
            # Распаковываем архив
            print(f"Распаковка архива: {archive_path}")
            shutil.unpack_archive(archive_path, temp_dir, "zip")
            
            # Загружаем метаданные
            metadata = self.metadata_manager.load_metadata(temp_dir / "metadata.json")
            compression_method = CompressionMethod(metadata["compression"]["method"])
            print(f"Метаданные загружены: {metadata}")
            
            # Распаковываем каждый файл
            for item in temp_dir.rglob("*"):
                if item.is_file() and item.name != "metadata.json":
                    relative_path = item.relative_to(temp_dir)
                    final_path = dest_path / relative_path
                    final_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    print(f"Восстановление файла: {relative_path}")
                    Compressor.decompress_file(
                        item,
                        final_path,
                        method=compression_method
                    )
            
            print("Восстановление завершено успешно")
            return dest_path
            
        except Exception as e:
            print(f"Ошибка при восстановлении: {e}")
            raise e
            
        finally:
            # Очищаем временные файлы
            try:
                if temp_dir.exists():
                    print(f"Очистка временной директории: {temp_dir}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Ошибка при очистке временных файлов: {e}")
                pass
                
    def verify_backup(self, backup_path: Union[str, Path], password: Optional[str] = None) -> bool:
        """
        Проверяет целостность резервной копии
        
        Args:
            backup_path: Путь к файлу резервной копии
            password: Пароль для расшифровки (если требуется)
            
        Returns:
            bool: True если копия корректна, False если повреждена
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            return False
            
        # Создаем временную директорию для проверки
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = self.backup_dir / f"verify_{timestamp}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Расшифровываем архив если нужно
            if password:
                try:
                    encrypted_path = backup_path
                    decrypted_path = temp_dir / "decrypted.zip"
                    Encryptor.decrypt_file(encrypted_path, decrypted_path, password)
                    archive_path = decrypted_path
                except Exception:
                    return False
            else:
                archive_path = backup_path
                
            try:
                # Распаковываем архив
                shutil.unpack_archive(archive_path, temp_dir, "zip")
                
                # Проверяем наличие метаданных
                metadata_path = temp_dir / "metadata.json"
                if not metadata_path.exists():
                    return False
                    
                # Загружаем метаданные
                try:
                    metadata = self.metadata_manager.load_metadata(metadata_path)
                except Exception:
                    return False
                
                # Проверяем каждый файл
                for item in temp_dir.rglob("*"):
                    if item.is_file() and item.name != "metadata.json":
                        try:
                            # Пробуем распаковать файл для проверки
                            compression_method = CompressionMethod(metadata["compression"]["method"])
                            test_path = temp_dir / f"test_{item.name}"
                            Compressor.decompress_file(item, test_path, method=compression_method)
                            test_path.unlink()  # Удаляем тестовый файл
                        except Exception:
                            return False
                            
                return True
                
            except Exception:
                return False
                
        finally:
            # Очищаем временные файлы
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
                
    def list_backups(self) -> List[Dict]:
        """
        Возвращает список всех резервных копий.
        """
        backups = []
        
        # Ищем файлы со всеми поддерживаемыми расширениями
        for extension in SUPPORTED_EXTENSIONS:
            for backup_file in self.backup_dir.glob(f"*{extension}"):
                try:
                    metadata = self._read_metadata(backup_file)
                    backups.append(metadata)
                except Exception as e:
                    print(f"Ошибка чтения метаданных {backup_file}: {e}")
                
        return sorted(backups, key=lambda x: x.get('backup_date', ''), reverse=True)

    def _read_metadata(self, backup_file: Path) -> Dict:
        # Создаем временную директорию для чтения метаданных
        temp_dir = self.backup_dir / f"list_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Пробуем прочитать метаданные без пароля
            try:
                shutil.unpack_archive(backup_file, temp_dir, "zip")
                metadata = self.metadata_manager.load_metadata(temp_dir / "metadata.json")
            except:
                # Если не получилось, значит файл зашифрован
                metadata = {
                    "name": backup_file.name,
                    "encrypted": True,
                    "backup_date": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                }
                
            metadata.update({
                "backup_file": str(backup_file),  # Полный путь к файлу
                "backup_size": backup_file.stat().st_size
            })
            return metadata
            
        finally:
            # Очищаем временные файлы
            if temp_dir.exists():
                shutil.rmtree(temp_dir) 