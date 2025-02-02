"""
Диалог для управления хранилищем резервных копий
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QGroupBox,
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from ..core.storage import StorageManager, StoragePolicy

class StorageDialog(QDialog):
    def __init__(self, backup_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление хранилищем")
        self.setMinimumSize(600, 400)
        
        # Инициализируем менеджер хранилища
        self.storage = StorageManager(backup_dir)
        
        # Создаем layout
        layout = QVBoxLayout(self)
        
        # Создаем группу с информацией о хранилище
        info_group = QGroupBox("Информация о хранилище")
        info_layout = QVBoxLayout(info_group)
        
        self.total_size_label = QLabel()
        self.backup_count_label = QLabel()
        self.oldest_backup_label = QLabel()
        self.newest_backup_label = QLabel()
        self.free_space_label = QLabel()
        
        info_layout.addWidget(self.total_size_label)
        info_layout.addWidget(self.backup_count_label)
        info_layout.addWidget(self.oldest_backup_label)
        info_layout.addWidget(self.newest_backup_label)
        info_layout.addWidget(self.free_space_label)
        
        layout.addWidget(info_group)
        
        # Создаем группу с политиками хранения
        policy_group = QGroupBox("Политики хранения")
        policy_layout = QVBoxLayout(policy_group)
        
        # Максимальный размер
        max_size_layout = QHBoxLayout()
        max_size_layout.addWidget(QLabel("Максимальный размер (ГБ):"))
        self.max_size_spin = QDoubleSpinBox()
        self.max_size_spin.setRange(0, 10000)
        self.max_size_spin.setSpecialValueText("Не ограничено")
        max_size_layout.addWidget(self.max_size_spin)
        policy_layout.addLayout(max_size_layout)
        
        # Максимальное количество копий
        max_backups_layout = QHBoxLayout()
        max_backups_layout.addWidget(QLabel("Максимальное количество копий:"))
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(0, 1000)
        self.max_backups_spin.setSpecialValueText("Не ограничено")
        max_backups_layout.addWidget(self.max_backups_spin)
        policy_layout.addLayout(max_backups_layout)
        
        # Срок хранения
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("Срок хранения (дней):"))
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(0, 3650)
        self.retention_spin.setSpecialValueText("Не ограничено")
        retention_layout.addWidget(self.retention_spin)
        policy_layout.addLayout(retention_layout)
        
        # Минимальное свободное место
        min_free_layout = QHBoxLayout()
        min_free_layout.addWidget(QLabel("Минимальное свободное место (ГБ):"))
        self.min_free_spin = QDoubleSpinBox()
        self.min_free_spin.setRange(0, 10000)
        self.min_free_spin.setSpecialValueText("Не ограничено")
        min_free_layout.addWidget(self.min_free_spin)
        policy_layout.addLayout(min_free_layout)
        
        layout.addWidget(policy_group)
        
        # Создаем кнопки управления
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self.apply_policy)
        button_layout.addWidget(apply_btn)
        
        cleanup_btn = QPushButton("Очистить")
        cleanup_btn.clicked.connect(self.cleanup_storage)
        button_layout.addWidget(cleanup_btn)
        
        layout.addLayout(button_layout)
        
        # Создаем прогресс-бар для очистки
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Загружаем текущие настройки
        self.load_current_settings()
        
        # Запускаем таймер обновления информации
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_storage_info)
        self.update_timer.start(5000)  # Обновляем каждые 5 секунд
        
        # Обновляем информацию сразу
        self.update_storage_info()
        
    def load_current_settings(self):
        """Загружает текущие настройки"""
        policy = self.storage.policy
        
        self.max_size_spin.setValue(policy.max_size_gb or 0)
        self.max_backups_spin.setValue(policy.max_backups or 0)
        self.retention_spin.setValue(policy.retention_days or 0)
        self.min_free_spin.setValue(policy.min_free_space_gb or 0)
        
    def update_storage_info(self):
        """Обновляет информацию о хранилище"""
        info = self.storage.get_storage_info()
        
        self.total_size_label.setText(f"Общий размер: {info['total_size_gb']:.2f} ГБ")
        self.backup_count_label.setText(f"Количество копий: {info['backup_count']}")
        
        if info['oldest_backup']:
            self.oldest_backup_label.setText(
                f"Самая старая копия: {info['oldest_backup']}"
            )
        else:
            self.oldest_backup_label.setText("Самая старая копия: нет")
            
        if info['newest_backup']:
            self.newest_backup_label.setText(
                f"Самая новая копия: {info['newest_backup']}"
            )
        else:
            self.newest_backup_label.setText("Самая новая копия: нет")
            
        self.free_space_label.setText(
            f"Свободное место: {info['free_space_gb']:.2f} ГБ"
        )
        
        # Проверяем политики
        policy_results = self.storage.check_storage_policy()
        if not all(policy_results.values()):
            self.setStyleSheet("QLabel { color: red; }")
        else:
            self.setStyleSheet("")
            
    def apply_policy(self):
        """Применяет новые политики хранения"""
        policy = StoragePolicy(
            max_size_gb=self.max_size_spin.value() or None,
            max_backups=self.max_backups_spin.value() or None,
            retention_days=self.retention_spin.value() or None,
            min_free_space_gb=self.min_free_spin.value() or None
        )
        
        self.storage.set_policy(policy)
        QMessageBox.information(self, "Успех", "Политики хранения обновлены")
        
    def cleanup_storage(self):
        """Запускает очистку хранилища"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите очистить хранилище в соответствии с политиками?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.progress.show()
            self.progress.setRange(0, 0)  # Бесконечный прогресс
            
            try:
                deleted_files = self.storage.cleanup()
                self.progress.hide()
                
                if deleted_files:
                    QMessageBox.information(
                        self,
                        "Успех",
                        f"Удалено файлов: {len(deleted_files)}\n\n" +
                        "\n".join(deleted_files)
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Информация",
                        "Нет файлов для удаления"
                    )
                    
            except Exception as e:
                self.progress.hide()
                QMessageBox.critical(self, "Ошибка", str(e))
                
            self.update_storage_info() 