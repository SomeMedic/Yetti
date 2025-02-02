"""
Модуль для сжатия файлов
"""
import zlib
import lzma
import shutil
from enum import Enum
from pathlib import Path
from typing import Union, BinaryIO

class CompressionMethod(str, Enum):
    """Методы сжатия"""
    ZLIB = "zlib"
    LZMA = "lzma"
    NONE = "none"

class Compressor:
    """Класс для сжатия и распаковки файлов"""
    
    CHUNK_SIZE = 8192  # Размер буфера для чтения/записи
    
    @staticmethod
    def compress_file(
        source: Union[str, Path],
        dest: Union[str, Path],
        method: CompressionMethod = CompressionMethod.ZLIB,
        level: int = 6
    ) -> None:
        """
        Сжимает файл
        
        Args:
            source: Путь к исходному файлу
            dest: Путь для сохранения сжатого файла
            method: Метод сжатия
            level: Уровень сжатия (1-9)
        """
        source = Path(source)
        dest = Path(dest)
        
        if not source.exists():
            raise FileNotFoundError(f"Файл не найден: {source}")
            
        if method == CompressionMethod.NONE:
            # Просто копируем файл без сжатия
            shutil.copy2(source, dest)
            return
            
        # Создаем компрессор
        if method == CompressionMethod.ZLIB:
            compressor = zlib.compressobj(level=level)
        elif method == CompressionMethod.LZMA:
            compressor = lzma.LZMACompressor(preset=level)
        else:
            raise ValueError(f"Неподдерживаемый метод сжатия: {method}")
            
        # Сжимаем файл по частям
        with open(source, 'rb') as src, open(dest, 'wb') as dst:
            while True:
                chunk = src.read(Compressor.CHUNK_SIZE)
                if not chunk:
                    break
                compressed = compressor.compress(chunk)
                if compressed:
                    dst.write(compressed)
            # Записываем оставшиеся данные
            compressed = compressor.flush()
            if compressed:
                dst.write(compressed)
    
    @staticmethod
    def decompress_file(
        source: Union[str, Path],
        dest: Union[str, Path],
        method: CompressionMethod = CompressionMethod.ZLIB
    ) -> None:
        """
        Распаковывает файл
        
        Args:
            source: Путь к сжатому файлу
            dest: Путь для сохранения распакованного файла
            method: Метод сжатия
        """
        source = Path(source)
        dest = Path(dest)
        
        if not source.exists():
            raise FileNotFoundError(f"Файл не найден: {source}")
            
        if method == CompressionMethod.NONE:
            # Просто копируем файл без распаковки
            shutil.copy2(source, dest)
            return
            
        # Создаем декомпрессор
        if method == CompressionMethod.ZLIB:
            decompressor = zlib.decompressobj()
        elif method == CompressionMethod.LZMA:
            decompressor = lzma.LZMADecompressor()
        else:
            raise ValueError(f"Неподдерживаемый метод сжатия: {method}")
            
        # Распаковываем файл по частям
        with open(source, 'rb') as src, open(dest, 'wb') as dst:
            while True:
                chunk = src.read(Compressor.CHUNK_SIZE)
                if not chunk:
                    break
                try:
                    decompressed = decompressor.decompress(chunk)
                    if decompressed:
                        dst.write(decompressed)
                except Exception as e:
                    raise ValueError(f"Ошибка распаковки: {e}")
            # Записываем оставшиеся данные
            try:
                decompressed = decompressor.flush()
                if decompressed:
                    dst.write(decompressed)
            except Exception as e:
                raise ValueError(f"Ошибка при завершении распаковки: {e}") 