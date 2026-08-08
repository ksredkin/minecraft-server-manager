<div align="center">
  <img src="logo.png" width="200" alt="Minecraft Server Manager Logo">

# ⛏️ Minecraft Server Manager

**Локальная панель управления Minecraft-сервером**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge\&logo=react\&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge\&logo=vite\&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge\&logo=poetry\&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge\&logo=pytest\&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=for-the-badge\&logo=ruff\&logoColor=black)
![Mypy](https://img.shields.io/badge/mypy-checked-1f425f?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen?style=for-the-badge)

</div>

## 📄 Описание

**Minecraft Server Manager (MSM)** — это fullstack-приложение для локального управления Minecraft-сервером через веб-интерфейс.

MSM объединяет backend на **FastAPI** и интерактивный frontend на **React**, позволяя управлять сервером, просматривать логи и состояние, работать с резервными копиями и плагинами, а также изменять настройки сервера прямо из панели.

## 📌 Скриншоты

<img src="home.png" width="700" alt="Главная панель">
<br></br>
<img src="terminal.png" width="700" alt="Консоль сервера">
<br></br>
<img src="players.png" width="700" alt="Игроки">
<br></br>
<img src="plugins.png" width="700" alt="Плагины">
<br></br>
<img src="backups.png" width="700" alt="Резервные копии">
<br></br>
<img src="settings.png" width="700" alt="Настройки сервера">

## ✨ Возможности

* 🖥️ **Управление сервером** — запуск, остановка, перезапуск и выполнение команд через веб-консоль.
* 📊 **Мониторинг** — статус сервера, игроки, версия Minecraft, uptime, использование RAM и CPU.
* 📜 **Логи в реальном времени** — потоковая передача логов через WebSocket прямо в интерфейс.
* 💾 **Резервные копии** — создание, восстановление и удаление backup-файлов.
* 🔌 **Управление плагинами** — поиск плагинов через Modrinth, просмотр информации, установка и удаление.
* ⚙️ **Настройки сервера** — редактирование `server.properties` и управление EULA прямо из веб-интерфейса.

## 🛠️ Технологии

**Backend:** Python 3.14, FastAPI, Uvicorn, HTTPX, WebSocket, Poetry, Pytest, Ruff, Mypy

**Frontend:** React, Vite, JavaScript, CSS, Lucide React

## 📊 Качество проекта

🧪 **Покрытие тестами:** 80%

🛠️ **Ruff** используется для линтинга и форматирования, **Mypy** — для статической проверки типов.

🏗️ Backend разделён на HTTP-слой и бизнес-логику с использованием сервисной архитектуры и Dependency Injection.

## 📋 Требования

Для запуска проекта понадобятся:

* **Python 3.14**
* **Poetry**
* **Node.js**
* **npm**
* Установленный Minecraft-сервер

## 🚀 Запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/ksredkin/minecraft-server-manager
cd minecraft-server-manager
```

### 2. Установить зависимости backend

```bash
poetry install --only main
```

### 3. Настроить backend

Укажите путь к Minecraft-серверу и параметры его запуска в:

```text
src/api/core/config.py
```

### 4. Запустить API

```bash
poetry run python -m src.api
```

API будет доступен по адресу:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### 5. Запустить frontend

```bash
cd ./src/frontend
npm install
npm run dev
```

После запуска откройте адрес, который выведет Vite в консоли.

## ⭐ Поддержка

Если проект оказался интересным или полезным — поставьте ⭐ на GitHub!
