"""
CLI интерфейс для Yetti
"""
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from .core.backup_engine import BackupEngine, get_default_backup_dir
from .core.compression import CompressionMethod
from .core.constants import EXTENSION_YETTI, EXTENSION_ONI, SUPPORTED_EXTENSIONS
import sys

console = Console()

@click.group()
def cli():
    """Yetti - инструмент для создания резервных копий"""
    pass

@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.option('--backup-dir', '-b', type=click.Path(), default=None,
              help='Директория для хранения резервных копий')
@click.option('--compression', '-c', type=click.Choice(['zlib', 'lzma', 'none']),
              default='zlib', help='Метод сжатия')
@click.option('--level', '-l', type=click.IntRange(1, 9), default=6,
              help='Уровень сжатия (1-9)')
@click.option('--password', '-p', type=str, help='Пароль для шифрования')
@click.option('--extension', '-e', type=click.Choice([EXTENSION_YETTI, EXTENSION_ONI]),
              default=EXTENSION_YETTI, help='Расширение файла резервной копии')
def backup(source, backup_dir, compression, level, password, extension):
    """Создать резервную копию файла или директории"""
    try:
        engine = BackupEngine(backup_dir)
        compression_method = CompressionMethod(compression)
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Создание резервной копии...", total=100)
            
            backup_path = engine.create_backup(
                source,
                compression_method=compression_method,
                compression_level=level,
                password=password,
                extension=extension
            )
            
            progress.update(task, completed=100)
            
        console.print(f"[green]✓[/green] Резервная копия создана: {backup_path}")
        console.print(f"[green]✓[/green] Имя бэкапа: {backup_path.stem}")
        
        # Проверяем целостность созданной копии
        console.print("[cyan]Проверка целостности...[/cyan]", end="\r")
        
        if engine.verify_backup(backup_path, password):
            console.print("[green]✓[/green] Проверка целостности успешна")
        else:
            console.print("[red]✗[/red] Ошибка: копия повреждена")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]✗[/red] Ошибка: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('backup_name', type=str)
@click.argument('dest', type=click.Path())
@click.option('--backup-dir', '-b', type=click.Path(), default=None,
              help='Директория для хранения резервных копий')
@click.option('--password', '-p', type=str, help='Пароль для расшифровки')
def restore(backup_name, dest, backup_dir, password):
    """Восстановить данные из резервной копии по имени"""
    try:
        engine = BackupEngine(backup_dir)
        backup_path = engine.get_backup_by_name(backup_name)
        
        if not backup_path:
            console.print(f"[red]✗[/red] Ошибка: бэкап с именем '{backup_name}' не найден")
            sys.exit(1)
            
        with Progress() as progress:
            task = progress.add_task("[cyan]Восстановление данных...", total=100)
            
            restored_path = engine.restore_backup(backup_path, dest, password)
            
            progress.update(task, completed=100)
            
        console.print(f"[green]✓[/green] Данные восстановлены: {restored_path}")
    except ValueError as e:
        console.print(f"[red]✗[/red] Ошибка: неверный пароль")
    except Exception as e:
        console.print(f"[red]✗[/red] Ошибка: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--backup-dir', '-b', type=click.Path(), default=None,
              help='Директория для хранения резервных копий')
def list(backup_dir):
    """Показать список резервных копий"""
    try:
        engine = BackupEngine(backup_dir)
        backups = engine.list_backups()
        
        if not backups:
            console.print("[yellow]Резервные копии не найдены[/yellow]")
            return
            
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Имя")
        table.add_column("Путь")
        table.add_column("Тип")
        table.add_column("Размер")
        table.add_column("Создан")
        table.add_column("Сжатие")
        table.add_column("Шифрование")
        
        for backup in backups:
            size_mb = backup['backup_size'] / (1024 * 1024)
            backup_path = Path(backup['backup_file'])
            
            compression_info = backup.get('compression', {'method': 'unknown'})
            compression = f"{compression_info.get('method', 'unknown')}"
            if compression != "none":
                compression += f" (level {compression_info.get('level', '?')})"
                
            table.add_row(
                backup_path.stem,  # Имя бэкапа
                str(backup_path),  # Полный путь
                backup.get('type', 'unknown'),
                f"{size_mb:.2f} MB",
                backup.get('backup_date', ''),
                compression,
                "✓" if backup.get('encrypted', False) else "✗"
            )
            
        console.print(table)
        console.print(f"\nДиректория бэкапов: {engine.backup_dir}")
    except Exception as e:
        console.print(f"[red]✗[/red] Ошибка: {str(e)}")
        if str(e):
            console.print(f"[red]Детали ошибки: {str(e)}[/red]")

@cli.command()
@click.argument('backup_file', type=click.Path(exists=True))
@click.option('--password', '-p', type=str, help='Пароль для расшифровки')
def verify(backup_file, password):
    """Проверить целостность резервной копии"""
    try:
        engine = BackupEngine(Path(backup_file).parent)
        
        console.print("[cyan]Проверка целостности...[/cyan]", end="\r")
        
        if engine.verify_backup(backup_file, password):
            console.print("[green]✓[/green] Резервная копия корректна")
        else:
            console.print("[red]✗[/red] Резервная копия повреждена")
            sys.exit(1)
                
    except Exception as e:
        console.print(f"[red]✗[/red] Ошибка: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 