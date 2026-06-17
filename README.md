# ⛏️ Minecraft Server Manager

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=for-the-badge&logo=ruff&logoColor=black)
![Mypy](https://img.shields.io/badge/mypy-checked-1f425f?style=for-the-badge)

## 📝 Описание

API для управления Minecraft-сервером через HTTP-запросы.

Проект разрабатывается как учебный pet-проект и предназначен для автоматизации базовых задач администрирования сервера: запуск, остановка, изменение настроек, создание резервных копий и управление плагинами.

## 🚀 Возможности

На данный момент реализовано:

- Запуск сервера
- Остановка сервера
- Перезапуск сервера
- Получение статуса сервера
- Выполнение команд сервера
- Просмотр настроек из `server.properties`
- Изменение настроек сервера
- Принятие или отклонение EULA
- Получение списка установленных плагинов
- Создание резервных копий сервера

## ⚙️ Технологии

- Python 3.14+
- Poetry
- FastAPI
- Uvicorn
- Pathlib
- Mypy
- Ruff

## 🚀 Запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/ksredkin/minecraft-server-manager
cd minecraft-server-manager
```

### 2. Установить зависимости

```bash
poetry install
```

### 3. Настройка

Перед запуском необходимо указать путь к серверу Minecraft и параметры запуска в `src/common/core/config.py`.

### 4. Запустить сервер

```bash
poetry run python -m src.api
```

После запуска документация FastAPI будет доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

## 💡 Планы

- Чтение логов сервера
- Просмотр последних строк лога
- Установка плагинов через API
- Интеграция с Modrinth
- Веб-интерфейс
- Docker-поддержка
- Восстановление сервера из резервной копии

## ⭐ Примечание

Если проект оказался полезным — можно поставить ⭐ на GitHub! 🚀
