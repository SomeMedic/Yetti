"""
Утилита для регистрации расширений файлов в Windows
"""
import os
import sys
import winreg
from pathlib import Path
from ..core.constants import EXTENSION_YETTI, EXTENSION_ONI

def get_icon_path() -> str:
    """Получает полный путь к иконке приложения"""
    # Получаем путь к директории с установленным пакетом
    package_dir = Path(__file__).parent.parent
    icon_path = package_dir / "gui" / "icons" / "yeti.ico"
    
    if not icon_path.exists():
        # Если .ico файл не существует, используем .png
        png_path = package_dir / "gui" / "icons" / "yeti.png"
        if not png_path.exists():
            raise FileNotFoundError("Файл иконки не найден")
        return str(png_path)
    
    return str(icon_path)

def register_extension(ext: str, icon_path: str):
    """
    Регистрирует расширение файла в Windows
    
    Args:
        ext: Расширение файла (например, '.yetti')
        icon_path: Путь к файлу иконки
    """
    try:
        # Создаем ключ для расширения
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{ext}") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "YettiBackup")
            
        # Создаем ключ для типа файла
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\YettiBackup") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"Yetti Backup File {ext}")
            
            # Добавляем иконку
            with winreg.CreateKey(key, "DefaultIcon") as icon_key:
                winreg.SetValue(icon_key, "", winreg.REG_SZ, icon_path)
                
            # Добавляем команды
            with winreg.CreateKey(key, "shell\\open\\command") as cmd_key:
                cmd = f'"{sys.executable}" -m yetti restore "%1"'
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, cmd)
                
        print(f"Расширение {ext} успешно зарегистрировано")
        
    except Exception as e:
        print(f"Ошибка при регистрации расширения {ext}: {e}")
        
def register_extensions():
    """Регистрирует все поддерживаемые расширения"""
    try:
        icon_path = get_icon_path()
        
        # Регистрируем оба расширения
        register_extension(EXTENSION_YETTI, icon_path)
        register_extension(EXTENSION_ONI, icon_path)
        
        # Обновляем иконки в проводнике
        os.system("ie4uinit.exe -show")
        
        print("Расширения успешно зарегистрированы")
        
    except Exception as e:
        print(f"Ошибка при регистрации расширений: {e}")
        
if __name__ == "__main__":
    # Проверяем, запущен ли скрипт с правами администратора
    if sys.platform == "win32":
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            
        if not is_admin:
            print("Для регистрации расширений требуются права администратора")
            if sys.version_info >= (3, 0):
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
            sys.exit()
            
    register_extensions() 