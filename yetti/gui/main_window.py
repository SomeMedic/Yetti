"""
Главное окно приложения
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar,
    QComboBox, QSpinBox, QLineEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QApplication, QHeaderView,
    QMenu, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QIcon, QPixmap
from ..core.backup_engine import BackupEngine, get_default_backup_dir
from ..core.compression import CompressionMethod
from .scheduler_dialog import SchedulerDialog
from .storage_dialog import StorageDialog
from .styles import MAIN_STYLE, CARD_STYLE
from ..core.constants import EXTENSION_YETTI, EXTENSION_ONI, FILE_FILTER

class StyledButton(QPushButton):
    """Кастомная кнопка с иконкой"""
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path:
            # Получаем абсолютный путь к директории с иконками
            icons_dir = os.path.join(os.path.dirname(__file__), "icons")
            icon_file = os.path.join(icons_dir, icon_path)
            # Проверяем существование SVG файла
            svg_file = icon_file.replace('.png', '.svg')
            if os.path.exists(svg_file):
                self.setIcon(QIcon(svg_file))
            elif os.path.exists(icon_file):
                self.setIcon(QIcon(icon_file))
            self.setIconSize(QSize(24, 24))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class Card(QFrame):
    """Карточка с информацией"""
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(CARD_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 12px; color: #7aa2f7;")
        layout.addWidget(self.title_label)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.value_label)
        
    def set_value(self, value: str):
        """Устанавливает значение карточки"""
        self.value_label.setText(value)

class BackupWorker(QThread):
    """Поток для выполнения операций с резервными копиями"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.is_running = False
        
    def run(self):
        self.is_running = True
        try:
            engine = BackupEngine(self.kwargs.get('backup_dir'))
            
            if self.operation == 'backup':
                self.status.emit("Создание резервной копии...")
                backup_path = engine.create_backup(
                    self.kwargs['source'],
                    compression_method=self.kwargs['compression_method'],
                    compression_level=self.kwargs['compression_level'],
                    password=self.kwargs.get('password'),
                    extension=self.kwargs.get('extension')
                )
                if self.is_running:
                    self.progress.emit(50)
                    self.status.emit("Проверка целостности...")
                    if engine.verify_backup(backup_path, self.kwargs.get('password')):
                        self.progress.emit(100)
                        self.finished.emit(True, str(backup_path))
                    else:
                        self.finished.emit(False, "Ошибка: копия повреждена")
                
            elif self.operation == 'restore':
                self.status.emit("Восстановление данных...")
                backup_path = engine.get_backup_by_name(self.kwargs['backup_name'])
                if not backup_path:
                    self.finished.emit(False, f"Бэкап с именем '{self.kwargs['backup_name']}' не найден")
                    return
                    
                restored_path = engine.restore_backup(
                    backup_path,
                    self.kwargs['dest'],
                    self.kwargs.get('password')
                )
                if self.is_running:
                    self.progress.emit(100)
                    self.finished.emit(True, str(restored_path))
                
            elif self.operation == 'verify':
                self.status.emit("Проверка целостности...")
                backup_path = engine.get_backup_by_name(self.kwargs['backup_name'])
                if not backup_path:
                    self.finished.emit(False, f"Бэкап с именем '{self.kwargs['backup_name']}' не найден")
                    return
                    
                result = engine.verify_backup(
                    backup_path,
                    self.kwargs.get('password')
                )
                if self.is_running:
                    self.progress.emit(100)
                    if result:
                        self.finished.emit(True, "Резервная копия корректна")
                    else:
                        self.finished.emit(False, "Резервная копия повреждена")
                
        except Exception as e:
            if self.is_running:
                self.finished.emit(False, str(e))
        finally:
            self.is_running = False
            
    def stop(self):
        """Останавливает выполнение операции"""
        self.is_running = False
        self.wait()

class BackupDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Существующие элементы интерфейса...

        # Добавляем выбор расширения
        extension_layout = QHBoxLayout()
        extension_label = QLabel("Расширение:")
        self.extension_combo = QComboBox()
        self.extension_combo.addItems([EXTENSION_YETTI, EXTENSION_ONI])
        extension_layout.addWidget(extension_label)
        extension_layout.addWidget(self.extension_combo)
        layout.addLayout(extension_layout)

        self.setLayout(layout)

    def get_values(self):
        return {
            'compression': self.compression_combo.currentText(),
            'level': self.level_spin.value(),
            'password': self.password_edit.text(),
            'extension': self.extension_combo.currentText()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Устанавливаем иконку приложения
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        icon_path = os.path.join(icons_dir, "yeti.png")
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)
        QApplication.setWindowIcon(app_icon)  # Устанавливаем иконку для всего приложения
        
        self.setWindowTitle("Yetti")
        self.setMinimumSize(1280, 720)
        self.setStyleSheet(MAIN_STYLE)
        
        # Инициализируем переменные для рабочих потоков
        self.current_worker = None
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Верхняя панель с информацией
        info_layout = QHBoxLayout()
        
        # Карточки с информацией
        self.total_backups = Card("Всего резервных копий", "0")
        self.total_size = Card("Общий размер", "0 MB")
        self.last_backup = Card("Последний бэкап", "Нет")
        
        info_layout.addWidget(self.total_backups)
        info_layout.addWidget(self.total_size)
        info_layout.addWidget(self.last_backup)
        main_layout.addLayout(info_layout)
        
        # Панель с кнопками
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.backup_btn = StyledButton("Создать резервную копию", "backup.svg")
        self.backup_btn.clicked.connect(self.show_backup_dialog)
        button_layout.addWidget(self.backup_btn)
        
        self.restore_btn = StyledButton("Восстановить", "restore.svg")
        self.restore_btn.clicked.connect(self.show_restore_dialog)
        button_layout.addWidget(self.restore_btn)
        
        self.verify_btn = StyledButton("Проверить", "verify.svg")
        self.verify_btn.clicked.connect(self.show_verify_dialog)
        button_layout.addWidget(self.verify_btn)
        
        button_layout.addStretch()
        
        self.scheduler_btn = StyledButton("Планировщик", "schedule.svg")
        self.scheduler_btn.clicked.connect(self.show_scheduler_dialog)
        button_layout.addWidget(self.scheduler_btn)
        
        self.storage_btn = StyledButton("Хранилище", "storage.svg")
        self.storage_btn.clicked.connect(self.show_storage_dialog)
        button_layout.addWidget(self.storage_btn)
        
        main_layout.addLayout(button_layout)
        
        # Таблица с резервными копиями
        table_container = QWidget()
        table_container.setObjectName("card")
        table_container.setStyleSheet(CARD_STYLE)
        table_layout = QVBoxLayout(table_container)
        
        table_header = QLabel("Резервные копии")
        table_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #7aa2f7;")
        table_layout.addWidget(table_header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Имя", "Путь", "Тип", "Размер", "Создан", "Сжатие", "Шифрование"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        table_layout.addWidget(self.table)
        
        main_layout.addWidget(table_container)
        
        # Создаем контекстное меню
        self.context_menu = QMenu(self)
        self.restore_action = self.context_menu.addAction("Восстановить")
        self.verify_action = self.context_menu.addAction("Проверить целостность")
        
        self.restore_action.triggered.connect(self.restore_selected)
        self.verify_action.triggered.connect(self.verify_selected)
        
        # Статус и прогресс
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel()
        self.status_label.hide()
        status_layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.hide()
        status_layout.addWidget(self.progress)
        
        main_layout.addLayout(status_layout)
        
        # Загружаем список резервных копий
        self.refresh_backup_list()
        
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.current_worker and self.current_worker.is_running:
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Операция еще выполняется. Вы уверены, что хотите закрыть приложение?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.current_worker.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
    def start_worker(self, worker: BackupWorker):
        """Запускает рабочий поток"""
        if self.current_worker and self.current_worker.is_running:
            self.current_worker.stop()
            
        self.current_worker = worker
        worker.progress.connect(self.on_progress)
        worker.status.connect(self.on_status)
        worker.finished.connect(self.on_worker_finished)
        worker.start()
        
        self.progress.setValue(0)
        self.progress.show()
        self.status_label.show()
        
    def on_progress(self, value: int):
        """Обработчик сигнала прогресса"""
        self.progress.setValue(value)
        
    def on_status(self, message: str):
        """Обработчик сигнала статуса"""
        self.status_label.setText(message)
        
    def on_worker_finished(self, success: bool, message: str):
        """Общий обработчик завершения операций"""
        self.progress.hide()
        self.status_label.hide()
        
        if self.current_worker:
            self.current_worker.stop()
            self.current_worker = None
            
        if success:
            QMessageBox.information(self, "Успех", message)
            self.refresh_backup_list()
        else:
            QMessageBox.critical(self, "Ошибка", message)
        
    def show_storage_dialog(self):
        """Показывает диалог управления хранилищем"""
        dialog = StorageDialog('./backups', self)
        dialog.exec()
        self.refresh_backup_list()
        
    def show_scheduler_dialog(self):
        """Показывает диалог планировщика"""
        dialog = SchedulerDialog(self)
        dialog.exec()
        
    def update_info_cards(self):
        """Обновляет информацию в карточках"""
        try:
            engine = BackupEngine()
            backups = engine.list_backups()
            
            if backups:
                total_size = sum(b.get('backup_size', 0) for b in backups) / (1024 * 1024)
                last_backup = max(backups, key=lambda x: x.get('backup_date', ''))
                last_backup_name = Path(last_backup.get('backup_file', '')).stem
                
                # Обновляем значения карточек
                self.total_backups.set_value(str(len(backups)))
                self.total_size.set_value(f"{total_size:.2f} MB")
                self.last_backup.set_value(last_backup_name)
            else:
                # Устанавливаем значения по умолчанию
                self.total_backups.set_value("0")
                self.total_size.set_value("0 MB")
                self.last_backup.set_value("Нет")
                
        except Exception as e:
            print(f"Ошибка при обновлении информации: {e}")
            # Устанавливаем значения по умолчанию в случае ошибки
            self.total_backups.set_value("0")
            self.total_size.set_value("0 MB")
            self.last_backup.set_value("Нет")
            
    def refresh_backup_list(self):
        """Обновляет список резервных копий"""
        try:
            engine = BackupEngine()
            backups = engine.list_backups()
            
            if backups is None:
                backups = []
            
            self.table.setRowCount(len(backups))
            for row, backup in enumerate(backups):
                size_mb = backup.get('backup_size', 0) / (1024 * 1024)
                backup_path = Path(backup.get('backup_file', ''))
                
                compression_info = backup.get('compression', {'method': 'unknown'})
                compression = f"{compression_info.get('method', 'unknown')}"
                if compression != "none":
                    compression += f" (level {compression_info.get('level', '?')})"
                    
                name_item = QTableWidgetItem(backup_path.stem)
                path_item = QTableWidgetItem(str(backup_path))
                type_item = QTableWidgetItem(backup.get('type', 'unknown'))
                size_item = QTableWidgetItem(f"{size_mb:.2f} MB")
                date_item = QTableWidgetItem(backup.get('backup_date', ''))
                compression_item = QTableWidgetItem(compression)
                encrypted_item = QTableWidgetItem("✓" if backup.get('encrypted', False) else "✗")
                
                # Устанавливаем выравнивание для каждой ячейки
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                path_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                compression_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                encrypted_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                
                # Добавляем подсказки
                name_item.setToolTip(backup_path.stem)
                path_item.setToolTip(str(backup_path))
                
                self.table.setItem(row, 0, name_item)
                self.table.setItem(row, 1, path_item)
                self.table.setItem(row, 2, type_item)
                self.table.setItem(row, 3, size_item)
                self.table.setItem(row, 4, date_item)
                self.table.setItem(row, 5, compression_item)
                self.table.setItem(row, 6, encrypted_item)
                
            # Устанавливаем размеры колонок
            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)
            
            # Обновляем информацию в карточках
            self.update_info_cards()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.table.setRowCount(0)
        
    def show_backup_dialog(self):
        """Показывает диалог создания резервной копии"""
        # Создаем диалог с возможностью выбора файлов и папок
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        
        # Добавляем кнопку для выбора директории
        layout = file_dialog.layout()
        dir_button = QPushButton("Выбрать директорию")
        layout.addWidget(dir_button, layout.rowCount(), 0, 1, -1)
        
        source = None
        
        def select_directory():
            nonlocal source
            dir_path = QFileDialog.getExistingDirectory(self, "Выберите директорию для резервного копирования")
            if dir_path:
                source = dir_path
                file_dialog.close()
                
        dir_button.clicked.connect(select_directory)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            source = file_dialog.selectedFiles()[0]
        
        if not source:
            return
            
        dialog = QWidget(self, Qt.WindowType.Window)
        dialog.setWindowTitle("Создание резервной копии")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Показываем выбранный путь
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Исходный путь:"))
        source_label = QLabel(source)
        source_label.setWordWrap(True)
        source_layout.addWidget(source_label)
        layout.addLayout(source_layout)
        
        # Директория для сохранения
        backup_dir_layout = QHBoxLayout()
        backup_dir_layout.addWidget(QLabel("Директория для сохранения:"))
        backup_dir_edit = QLineEdit(str(get_default_backup_dir()))
        backup_dir_btn = QPushButton("Обзор")
        
        def choose_backup_dir():
            dir_path = QFileDialog.getExistingDirectory(
                dialog, "Выберите директорию для сохранения резервных копий",
                backup_dir_edit.text()
            )
            if dir_path:
                backup_dir_edit.setText(dir_path)
                
        backup_dir_btn.clicked.connect(choose_backup_dir)
        backup_dir_layout.addWidget(backup_dir_edit)
        backup_dir_layout.addWidget(backup_dir_btn)
        layout.addLayout(backup_dir_layout)
        
        # Метод сжатия
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(QLabel("Метод сжатия:"))
        compression_combo = QComboBox()
        compression_combo.addItems(['zlib', 'lzma', 'none'])
        compression_layout.addWidget(compression_combo)
        layout.addLayout(compression_layout)
        
        # Уровень сжатия
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Уровень сжатия:"))
        level_spin = QSpinBox()
        level_spin.setRange(1, 9)
        level_spin.setValue(6)
        level_layout.addWidget(level_spin)
        layout.addLayout(level_layout)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_edit)
        layout.addLayout(password_layout)
        
        # Добавляем выбор расширения
        extension_layout = QHBoxLayout()
        extension_label = QLabel("Расширение:")
        self.extension_combo = QComboBox()
        self.extension_combo.addItems([EXTENSION_YETTI, EXTENSION_ONI])
        extension_layout.addWidget(extension_label)
        extension_layout.addWidget(self.extension_combo)
        layout.addLayout(extension_layout)
        
        # Кнопка создания
        create_btn = QPushButton("Создать")
        layout.addWidget(create_btn)
        
        def create_backup():
            worker = BackupWorker(
                'backup',
                source=source,
                backup_dir=backup_dir_edit.text(),
                compression_method=CompressionMethod(compression_combo.currentText()),
                compression_level=level_spin.value(),
                password=password_edit.text() or None,
                extension=self.extension_combo.currentText()
            )
            self.start_worker(worker)
            dialog.close()
            
        create_btn.clicked.connect(create_backup)
        dialog.show()
        
    def show_restore_dialog(self):
        """Показывает диалог восстановления"""
        backup_name = self.get_selected_backup_name()
        if not backup_name:
            # Если файл не выбран, показываем диалог выбора файла
            backup_file = QFileDialog.getOpenFileName(
                self, "Выберите файл резервной копии", filter="Yetti files (*.yetti)"
            )[0]
            if not backup_file:
                return
            backup_name = Path(backup_file).stem
            
        dest = QFileDialog.getExistingDirectory(
            self, "Выберите директорию для восстановления"
        )
        if not dest:
            return
            
        dialog = QWidget(self, Qt.WindowType.Window)
        dialog.setWindowTitle("Восстановление")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_edit)
        layout.addLayout(password_layout)
        
        # Кнопка восстановления
        restore_btn = QPushButton("Восстановить")
        layout.addWidget(restore_btn)
        
        def restore_backup():
            worker = BackupWorker(
                'restore',
                backup_name=backup_name,
                dest=dest,
                password=password_edit.text() or None
            )
            self.start_worker(worker)
            dialog.close()
            
        restore_btn.clicked.connect(restore_backup)
        dialog.show()
        
    def show_verify_dialog(self):
        """Показывает диалог проверки"""
        backup_name = self.get_selected_backup_name()
        if not backup_name:
            # Если файл не выбран, показываем диалог выбора файла
            backup_file = QFileDialog.getOpenFileName(
                self, "Выберите файл резервной копии", filter="Yetti files (*.yetti)"
            )[0]
            if not backup_file:
                return
            backup_name = Path(backup_file).stem
            
        dialog = QWidget(self, Qt.WindowType.Window)
        dialog.setWindowTitle("Проверка")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_edit)
        layout.addLayout(password_layout)
        
        # Кнопка проверки
        verify_btn = QPushButton("Проверить")
        layout.addWidget(verify_btn)
        
        def verify_backup():
            worker = BackupWorker(
                'verify',
                backup_name=backup_name,
                password=password_edit.text() or None
            )
            self.start_worker(worker)
            dialog.close()
            
        verify_btn.clicked.connect(verify_backup)
        dialog.show()
        
    def show_context_menu(self, pos: QPoint):
        """Показывает контекстное меню для выбранного файла"""
        if self.table.selectedItems():
            self.context_menu.exec(self.table.viewport().mapToGlobal(pos))
            
    def get_selected_backup_name(self) -> str:
        """Возвращает имя выбранного бэкапа"""
        row = self.table.currentRow()
        if row >= 0:
            return self.table.item(row, 0).text()
        return ""
        
    def restore_selected(self):
        """Восстанавливает выбранный бэкап"""
        backup_name = self.get_selected_backup_name()
        if not backup_name:
            return
            
        dest = QFileDialog.getExistingDirectory(
            self, "Выберите директорию для восстановления"
        )
        if not dest:
            return
            
        dialog = QWidget(self, Qt.WindowType.Window)
        dialog.setWindowTitle("Восстановление")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_edit)
        layout.addLayout(password_layout)
        
        # Кнопка восстановления
        restore_btn = QPushButton("Восстановить")
        layout.addWidget(restore_btn)
        
        def restore_backup():
            worker = BackupWorker(
                'restore',
                backup_name=backup_name,
                dest=dest,
                password=password_edit.text() or None
            )
            self.start_worker(worker)
            dialog.close()
            
        restore_btn.clicked.connect(restore_backup)
        dialog.show()
        
    def verify_selected(self):
        """Проверяет целостность выбранного бэкапа"""
        backup_name = self.get_selected_backup_name()
        if not backup_name:
            return
            
        dialog = QWidget(self, Qt.WindowType.Window)
        dialog.setWindowTitle("Проверка")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_edit)
        layout.addLayout(password_layout)
        
        # Кнопка проверки
        verify_btn = QPushButton("Проверить")
        layout.addWidget(verify_btn)
        
        def verify_backup():
            worker = BackupWorker(
                'verify',
                backup_name=backup_name,
                password=password_edit.text() or None
            )
            self.start_worker(worker)
            dialog.close()
            
        verify_btn.clicked.connect(verify_backup)
        dialog.show() 