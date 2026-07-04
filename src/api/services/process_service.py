from collections import deque
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Event, Thread

from src.common.core.config import (
    JAR_ARGS,
    JAR_NAME,
    JAVA,
    JAVA_ARGS,
    MINECRAFT_VERSION,
    SERVER_PATH,
    SERVER_STOP_TIMEOUT,
)
from src.common.exceptions.server import (
    InvalidServerConfigurationError,
    ServerAlreadyRunningError,
    ServerFolderDoesNotExistError,
    ServerNotRunningError,
    ServerResponseTimeoutError,
    ServerStopTimeoutError,
)


class ProcessService:
    def __init__(self, server_path: str = SERVER_PATH):
        if not server_path:
            raise InvalidServerConfigurationError(
                "В конфиге не установлен путь к серверу."
            )

        self.server_dir = Path(server_path)

        if not self.server_dir.exists():
            raise ServerFolderDoesNotExistError("Папки сервера не существует.")

        self._process: Popen[str] | None = None
        self._status = None
        self._logs: deque[str] = deque(maxlen=1000)
        self._players: list[str] = []
        self._players_event: Event = Event()
        self._stop_event: Event = Event()

    def start(self) -> bool:
        if not self._process or self._process.poll() is not None:
            if not self.server_dir.exists():
                raise ServerFolderDoesNotExistError("Папки сервера не существует.")

            if not JAVA:
                raise InvalidServerConfigurationError("В конфиге не указана java.")

            if not JAR_NAME:
                raise InvalidServerConfigurationError(
                    "В конфиге не указано имя jar файла."
                )

            start_command = [JAVA, *JAVA_ARGS, "-jar", JAR_NAME, *JAR_ARGS]
            self._process = Popen(
                start_command,
                cwd=str(self.server_dir),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )

            Thread(target=self._reader, daemon=True).start()

            return True
        raise ServerAlreadyRunningError("Сервер уже запущен.")

    def stop(self) -> None:
        self.execute_command("stop")

    def restart(self) -> bool:
        self._stop_event.clear()
        self.stop()

        if not self._stop_event.wait(timeout=SERVER_STOP_TIMEOUT):
            raise ServerStopTimeoutError(
                f"Сервер не остановился за {SERVER_STOP_TIMEOUT} секунд."
            )

        return self.start()

    def status(self) -> str:
        if self._process is None:
            return "stopped"

        if self._process.poll() is None:
            return "running"

        return "stopped"

    def execute_command(self, command: str) -> None:
        if not self._process or self._process.poll() is not None:
            raise ServerNotRunningError("Сервер не запущен.")

        self._process.stdin.write(command + "\n")  # type: ignore
        self._process.stdin.flush()  # type: ignore

    def get_players(self) -> list[str] | None:
        if not self._process or self._process.poll() is not None:
            raise ServerNotRunningError("Сервер не запущен.")

        self._players_event.clear()
        self.execute_command("list")

        if not self._players_event.wait(timeout=5):
            raise ServerResponseTimeoutError("Сервер не ответил на команду list.")

        return self._players

    def get_server_info(self) -> dict[str, str | list[str] | None]:
        if not self._process or self._process.poll() is not None:
            return {"status": "stopped", "minecraft_version": MINECRAFT_VERSION}

        try:
            players = self.get_players()
        except ServerResponseTimeoutError, ServerNotRunningError:
            players = None

        info = {
            "status": self.status(),
            "players": players,
            "minecraft_version": MINECRAFT_VERSION,
        }
        return info

    def _reader(self) -> None:
        if self._process is None:
            return

        while True:
            line = self._process.stdout.readline()  # type: ignore

            if not line:
                self._stop_event.set()
                break

            self._logs.append(line)

            if "players online: " in line:
                self._players = line.split("players online: ")[1].split()
                self._players_event.set()

    def get_logs(self) -> list[str]:
        return list(self._logs)


process_service = ProcessService()


def get_process_service() -> ProcessService:
    return process_service
