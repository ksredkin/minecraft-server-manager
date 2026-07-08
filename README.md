# ⛏️ Minecraft Server Manager

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=for-the-badge&logo=ruff&logoColor=black)
![Mypy](https://img.shields.io/badge/mypy-checked-1f425f?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Coverage-82%25-brightgreen?style=for-the-badge)

## 📝 Описание

**Minecraft Server Manager** - Fullstack-приложение для управления Minecraft-сервером.

Проект включает управление сервером, настройками, резервными копиями, плагинами и потоковую передачу логов в реальном времени.

## ✨ Основные возможности

- Управление сервером (запуск, остановка, перезапуск)
- Выполнение консольных команд
- Получение информации о сервере и игроках
- Работа с `server.properties`
- Управление EULA
- Создание и восстановление резервных копий
- Установка плагинов через Modrinth API
- Просмотр логов сервера
- Передача логов через WebSocket в режиме реального времени
- Автоматическая обработка ошибок с понятными HTTP-ответами

## 🛠️ Используемые технологии

- Python 3.14
- FastAPI
- Uvicorn
- Poetry
- HTTPX
- WebSocket
- Ruff
- Mypy
- Pytest

## ✅ Качество проекта

- Статическая проверка типов с помощью **mypy**
- Проверка стиля кода с помощью **Ruff**
- Покрытие тестами **82%**
- Разделение бизнес-логики и HTTP-слоя
- Использование dependency injection (`Depends`) и сервисной архитектуры

## 🚀 Запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/ksredkin/minecraft-server-manager
cd minecraft-server-manager
```

### 2. Установить зависимости

```bash
poetry install --only main
```

### 3. Настроить проект

Перед запуском необходимо указать путь к серверу Minecraft и параметры запуска в:

```text
src/api/core/config.py
```

### 4. Запустить API

```bash
poetry run python -m src.api
```

После запуска документация FastAPI будет доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

## 💡 Планы

- Веб-интерфейс
- Docker-поддержка

## ⭐ Поддержка

Если проект оказался интересным или полезным - поставьте ⭐ на GitHub.