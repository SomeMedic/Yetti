# Yetti

Yetti - это мощный инструмент для создания резервных копий файлов и директорий.

## Установка

```bash
pip install -e .
```

## Использование

### Создание резервной копии

```bash
yetti backup path/to/file --backup-dir backups/
```

### Просмотр списка резервных копий

```bash
yetti list --backup-dir backups/
```

## Особенности

- Создание резервных копий файлов и директорий
- Хранение метаданных
- Удобный CLI интерфейс
- Форматированный вывод информации

## Требования

- Python 3.8+
- click
- rich
- cryptography
- tqdm

## Разработка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте окружение: 
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Установите зависимости: `pip install -r requirements.txt`
5. Установите пакет в режиме разработки: `pip install -e .` 