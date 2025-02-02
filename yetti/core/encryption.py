"""
Модуль для шифрования данных
"""
import os
from pathlib import Path
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class Encryptor:
    CHUNK_SIZE = 64 * 1024  # 64KB chunks
    
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        """
        Генерирует ключ шифрования из пароля
        
        Args:
            password: Пароль для генерации ключа
            salt: Соль для генерации ключа (если None, генерируется случайная)
            
        Returns:
            bytes: Ключ шифрования
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
        
    @staticmethod
    def encrypt_file(
        source: Union[str, Path],
        dest: Union[str, Path],
        password: str
    ) -> tuple[int, bytes]:
        """
        Шифрует файл
        
        Args:
            source: Путь к исходному файлу
            dest: Путь для зашифрованного файла
            password: Пароль для шифрования
            
        Returns:
            tuple[int, bytes]: (размер зашифрованного файла, соль)
        """
        source_path = Path(source)
        dest_path = Path(dest)
        
        # Генерируем ключ
        key, salt = Encryptor.generate_key(password)
        f = Fernet(key)
        
        # Записываем соль в начало файла
        with open(dest_path, 'wb') as df:
            df.write(salt)
            
            # Шифруем и записываем данные
            with open(source_path, 'rb') as sf:
                while True:
                    chunk = sf.read(Encryptor.CHUNK_SIZE)
                    if not chunk:
                        break
                    encrypted = f.encrypt(chunk)
                    df.write(encrypted)
                    
        return dest_path.stat().st_size, salt
        
    @staticmethod
    def decrypt_file(
        source: Union[str, Path],
        dest: Union[str, Path],
        password: str
    ) -> int:
        """
        Расшифровывает файл
        
        Args:
            source: Путь к зашифрованному файлу
            dest: Путь для расшифрованного файла
            password: Пароль для расшифровки
            
        Returns:
            int: Размер расшифрованного файла
        """
        source_path = Path(source)
        dest_path = Path(dest)
        
        with open(source_path, 'rb') as sf:
            # Читаем соль из начала файла
            salt = sf.read(16)
            
            # Генерируем ключ
            key, _ = Encryptor.generate_key(password, salt)
            f = Fernet(key)
            
            with open(dest_path, 'wb') as df:
                while True:
                    chunk = sf.read(Encryptor.CHUNK_SIZE)
                    if not chunk:
                        break
                    try:
                        decrypted = f.decrypt(chunk)
                        df.write(decrypted)
                    except Exception as e:
                        raise ValueError("Неверный пароль или поврежденный файл") from e
                    
        return dest_path.stat().st_size 