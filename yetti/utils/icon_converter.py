"""
Утилита для конвертации PNG в ICO
"""
from PIL import Image
import os
from pathlib import Path

def png_to_ico(png_path: str, ico_path: str = None):
    """
    Конвертирует PNG файл в ICO
    
    Args:
        png_path: Путь к PNG файлу
        ico_path: Путь для сохранения ICO файла (если None, сохраняет рядом с PNG)
    """
    if ico_path is None:
        ico_path = str(Path(png_path).with_suffix('.ico'))
        
    try:
        # Открываем изображение
        img = Image.open(png_path)
        
        # Создаем набор размеров для иконки
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        
        # Создаем копии изображения разных размеров
        img.save(ico_path, format='ICO', sizes=sizes)
        
        print(f"ICO файл успешно создан: {ico_path}")
        return ico_path
        
    except Exception as e:
        print(f"Ошибка при конвертации PNG в ICO: {e}")
        return None

if __name__ == "__main__":
    # Конвертируем иконку приложения
    package_dir = Path(__file__).parent.parent
    png_path = package_dir / "gui" / "icons" / "yeti.png"
    
    if png_path.exists():
        png_to_ico(str(png_path)) 