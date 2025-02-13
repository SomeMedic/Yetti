from setuptools import setup, find_packages, Command
import sys
import os
import site
import winreg

# Пытаемся импортировать cx_Freeze, но не вызываем ошибку, если его нет
try:
    from cx_Freeze import setup, Executable
    has_cx_freeze = True
except ImportError:
    has_cx_freeze = False

def get_scripts_path():
    """Получает путь к директории со скриптами Python"""
    if hasattr(site, 'getusersitepackages'):
        user_scripts = os.path.join(site.getusersitepackages(), '..', 'Scripts')
        if os.path.exists(user_scripts):
            return user_scripts
    return None

def modify_path(add=True):
    """
    Добавляет или удаляет путь к скриптам Python из PATH
    
    Args:
        add: True для добавления, False для удаления
    """
    if sys.platform != "win32":
        return

    scripts_path = get_scripts_path()
    if not scripts_path:
        return

    try:
        # Открываем ключ PATH в реестре
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                path = winreg.QueryValueEx(key, "Path")[0]
            except WindowsError:
                path = ""

            paths = path.split(";") if path else []
            scripts_path = os.path.normpath(scripts_path)
            
            if add:
                if scripts_path not in paths:
                    paths.append(scripts_path)
                    print(f"Добавление {scripts_path} в PATH")
            else:
                if scripts_path in paths:
                    paths.remove(scripts_path)
                    print(f"Удаление {scripts_path} из PATH")

            # Обновляем PATH
            new_path = ";".join(filter(None, paths))
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)

            # Уведомляем систему об изменениях
            os.system('setx PATH "%PATH%"')
            
    except Exception as e:
        print(f"Ошибка при модификации PATH: {e}")

class RegisterExtensionsCommand(Command):
    """Команда для регистрации расширений файлов в Windows"""
    description = "Регистрация расширений файлов .yetti и .👹 в Windows"
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass
        
    def run(self):
        if sys.platform != "win32":
            print("Регистрация расширений поддерживается только в Windows")
            return
            
        try:
            from yetti.utils.icon_converter import png_to_ico
            from yetti.utils.register_extensions import register_extensions
            
            # Конвертируем PNG в ICO если нужно
            package_dir = os.path.dirname(os.path.abspath(__file__))
            png_path = os.path.join(package_dir, "yetti", "gui", "icons", "yeti.png")
            if os.path.exists(png_path):
                png_to_ico(png_path)
                
            # Регистрируем расширения
            register_extensions()
            
        except Exception as e:
            print(f"Ошибка при регистрации расширений: {e}")

class PostInstallCommand(Command):
    """Команда для пост-установочных действий"""
    description = "Выполняет пост-установочные действия (регистрация расширений, добавление в PATH)"
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass
        
    def run(self):
        # Добавляем путь в PATH
        modify_path(add=True)
        
        # Регистрируем расширения файлов
        if sys.platform == "win32":
            try:
                from yetti.utils.icon_converter import png_to_ico
                from yetti.utils.register_extensions import register_extensions
                
                # Конвертируем PNG в ICO если нужно
                package_dir = os.path.dirname(os.path.abspath(__file__))
                png_path = os.path.join(package_dir, "yetti", "gui", "icons", "yeti.png")
                if os.path.exists(png_path):
                    png_to_ico(png_path)
                    
                # Регистрируем расширения
                register_extensions()
                
            except Exception as e:
                print(f"Ошибка при регистрации расширений: {e}")

class UninstallCommand(Command):
    """Команда для действий при удалении"""
    description = "Выполняет действия при удалении (удаление из PATH)"
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass
        
    def run(self):
        # Удаляем путь из PATH
        modify_path(add=False)

# Базовые настройки для создания исполняемого файла
executables = []
options = {}

if has_cx_freeze:
    base = None
    if sys.platform == "win32":
        base = "Win32GUI"

    build_exe_options = {
        "packages": ["PyQt6"],
        "excludes": ["tkinter", "unittest", "email", "http", "xml", "pydoc"],
        "include_files": [
            ("yetti/gui/icons/yeti.png", "icons/yeti.png")
        ],
        "include_msvcr": True,
    }

    # Настройки иконок для Windows
    icon_path = "yetti/gui/icons/yeti.png"
    shortcut_table = [
        ("DesktopShortcut",        # Shortcut
         "DesktopFolder",          # Directory_
         "Yetti",                  # Name
         "TARGETDIR",              # Component_
         "[TARGETDIR]Yetti.exe",   # Target
         None,                     # Arguments
         None,                     # Description
         None,                     # Hotkey
         icon_path,                # Icon
         None,                     # IconIndex
         None,                     # ShowCmd
         "TARGETDIR"               # WkDir
         ),
        ("StartMenuShortcut",      # Shortcut
         "StartMenuFolder",        # Directory_
         "Yetti",                  # Name
         "TARGETDIR",              # Component_
         "[TARGETDIR]Yetti.exe",   # Target
         None,                     # Arguments
         None,                     # Description
         None,                     # Hotkey
         icon_path,                # Icon
         None,                     # IconIndex
         None,                     # ShowCmd
         "TARGETDIR"               # WkDir
         )
    ]

    msi_data = {
        "Shortcut": shortcut_table
    }

    executables = [
        Executable(
            "run.py",
            base=base,
            target_name="Yetti",
            icon=icon_path,
            shortcut_name="Yetti Backup",
            shortcut_dir="DesktopFolder"
        )
    ]

    options = {
        'build_exe': build_exe_options,
        'bdist_msi': {
            'install_icon': icon_path,
            'data': msi_data,
            'add_to_path': True,
            'initial_target_dir': r'[ProgramFilesFolder]\Yetti',
        }
    }

setup(
    name="yetti",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'yetti.gui': ['icons/*.png', 'icons/*.svg', 'icons/*.ico'],
    },
    install_requires=[
        'click>=8.1.7',
        'rich>=13.7.0',
        'cryptography>=41.0.7',
        'tqdm>=4.66.1',
        'PyQt6>=6.4.0',
        'schedule>=1.2.0',
        'pillow>=10.0.0',  # Для конвертации PNG в ICO
    ],
    options=options,
    executables=executables,
    author="SomeMedic",
    description="Инструмент для создания резервных копий",
    keywords="backup, archive, files",
    python_requires=">=3.8",
    cmdclass={
        'register_extensions': RegisterExtensionsCommand,
        'post_install': PostInstallCommand,
        'uninstall': UninstallCommand,
    },
    entry_points={
        'console_scripts': [
            'yetti=yetti.__main__:main',
            'yetti-gui=yetti.__main__:main_gui',
        ],
    },
) 