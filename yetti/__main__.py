"""
Точка входа для запуска приложения
"""
import sys
from PyQt6.QtWidgets import QApplication
from .gui import MainWindow
from .cli import cli

def main():
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Если есть аргументы, запускаем CLI
        cli()
    else:
        # Иначе запускаем GUI
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

if __name__ == '__main__':
    main() 