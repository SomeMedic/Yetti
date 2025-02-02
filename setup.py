from setuptools import setup, find_packages
from cx_Freeze import setup, Executable
import sys

# Базовые настройки для создания исполняемого файла
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

setup(
    name="yetti",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'yetti.gui': ['icons/*.png', 'icons/*.svg'],
    },
    install_requires=[
        'click>=8.1.7',
        'rich>=13.7.0',
        'cryptography>=41.0.7',
        'tqdm>=4.66.1',
        'PyQt6>=6.4.0',
        'schedule>=1.2.0',
    ],
    options={
        'build_exe': build_exe_options,
        'bdist_msi': {
            'install_icon': icon_path,
            'data': msi_data,
            'add_to_path': True,
            'initial_target_dir': r'[ProgramFilesFolder]\Yetti',
        }
    },
    executables=executables,
    author="SomeMedic",
    description="Инструмент для создания резервных копий",
    keywords="backup, archive, files",
    python_requires=">=3.8",
) 