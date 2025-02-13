"""
Точка входа для запуска приложения
"""
import sys
from PyQt6.QtWidgets import QApplication
from .gui import MainWindow
from .cli import cli

def main_gui():
    """Запускает графический интерфейс"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

def main():
    """Точка входа для CLI"""
    cli()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main()  # Запускаем CLI если есть аргументы
    else:
        main_gui()  # Иначе запускаем GUI 