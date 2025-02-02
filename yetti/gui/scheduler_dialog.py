"""
Диалог для управления планировщиком резервных копий
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QSpinBox, QLineEdit,
    QTableWidget, QTableWidgetItem, QTimeEdit,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTime
from ..core.scheduler import BackupTask, BackupScheduler

class SchedulerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Планировщик резервных копий")
        self.setMinimumSize(800, 400)
        
        # Инициализируем планировщик
        self.scheduler = BackupScheduler()
        
        # Создаем layout
        layout = QVBoxLayout(self)
        
        # Создаем таблицу задач
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Источник", "Директория", "Расписание", "Сжатие",
            "Уровень", "Шифрование"
        ])
        layout.addWidget(self.table)
        
        # Создаем кнопки управления
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.show_add_dialog)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Удалить")
        remove_btn.clicked.connect(self.remove_task)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        # Загружаем список задач
        self.refresh_task_list()
        
    def refresh_task_list(self):
        """Обновляет список задач"""
        tasks = self.scheduler.get_tasks()
        self.table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            self.table.setItem(row, 0, QTableWidgetItem(task.source))
            self.table.setItem(row, 1, QTableWidgetItem(task.backup_dir))
            
            schedule_text = f"{task.schedule_type}: {task.schedule_value}"
            self.table.setItem(row, 2, QTableWidgetItem(schedule_text))
            
            self.table.setItem(row, 3, QTableWidgetItem(task.compression_method))
            self.table.setItem(row, 4, QTableWidgetItem(str(task.compression_level)))
            self.table.setItem(row, 5, QTableWidgetItem(
                "✓" if task.password else "✗"
            ))
            
    def show_add_dialog(self):
        """Показывает диалог добавления задачи"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить задачу")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Источник
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Источник:"))
        source_btn = QPushButton("Выбрать...")
        source_path = QLineEdit()
        source_path.setReadOnly(True)
        
        def choose_source():
            path = QFileDialog.getExistingDirectory(
                dialog, "Выберите источник для резервного копирования"
            )
            if path:
                source_path.setText(path)
                
        source_btn.clicked.connect(choose_source)
        source_layout.addWidget(source_path)
        source_layout.addWidget(source_btn)
        layout.addLayout(source_layout)
        
        # Директория для резервных копий
        backup_dir_layout = QHBoxLayout()
        backup_dir_layout.addWidget(QLabel("Директория для копий:"))
        backup_dir_btn = QPushButton("Выбрать...")
        backup_dir_path = QLineEdit()
        backup_dir_path.setReadOnly(True)
        
        def choose_backup_dir():
            path = QFileDialog.getExistingDirectory(
                dialog, "Выберите директорию для резервных копий"
            )
            if path:
                backup_dir_path.setText(path)
                
        backup_dir_btn.clicked.connect(choose_backup_dir)
        backup_dir_layout.addWidget(backup_dir_path)
        backup_dir_layout.addWidget(backup_dir_btn)
        layout.addLayout(backup_dir_layout)
        
        # Тип расписания
        schedule_layout = QHBoxLayout()
        schedule_layout.addWidget(QLabel("Расписание:"))
        schedule_type = QComboBox()
        schedule_type.addItems(["daily", "weekly", "monthly"])
        schedule_layout.addWidget(schedule_type)
        
        # Время
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        schedule_layout.addWidget(time_edit)
        
        # День недели/месяца
        day_combo = QComboBox()
        day_combo.hide()
        schedule_layout.addWidget(day_combo)
        
        def on_schedule_type_changed():
            if schedule_type.currentText() == "daily":
                day_combo.hide()
            else:
                day_combo.show()
                if schedule_type.currentText() == "weekly":
                    day_combo.clear()
                    day_combo.addItems([
                        "Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"
                    ])
                else:
                    day_combo.clear()
                    day_combo.addItems([str(i) for i in range(1, 32)])
                    
        schedule_type.currentTextChanged.connect(on_schedule_type_changed)
        layout.addLayout(schedule_layout)
        
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
        
        # Кнопки
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def add_task():
            if not source_path.text():
                QMessageBox.warning(dialog, "Ошибка", "Выберите источник")
                return
                
            if not backup_dir_path.text():
                QMessageBox.warning(dialog, "Ошибка", "Выберите директорию для копий")
                return
                
            schedule_value = time_edit.time().toString("HH:mm")
            if schedule_type.currentText() != "daily":
                schedule_value = f"{day_combo.currentText()} {schedule_value}"
                
            task = BackupTask(
                source=source_path.text(),
                backup_dir=backup_dir_path.text(),
                schedule_type=schedule_type.currentText(),
                schedule_value=schedule_value,
                compression_method=compression_combo.currentText(),
                compression_level=level_spin.value(),
                password=password_edit.text() or None
            )
            
            self.scheduler.add_task(task)
            self.refresh_task_list()
            dialog.accept()
            
        ok_btn.clicked.connect(add_task)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
        
    def remove_task(self):
        """Удаляет выбранную задачу"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            tasks = self.scheduler.get_tasks()
            if current_row < len(tasks):
                task = tasks[current_row]
                self.scheduler.remove_task(task.task_id)
                self.refresh_task_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для удаления") 