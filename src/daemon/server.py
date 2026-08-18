import time
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from subprocess import PIPE, Popen
from threading import Event, Thread

from src.common.utils.logger import Logger
from src.daemon.exceptions.config import InvalidConfigError
from src.daemon.exceptions.server import (
    ServerFolderDoesNotExistError,
    ServerIsAlreadyRunningError,
    ServerIsNotRunningError,
    ServerJarDoesNotExistError,
    ServerResponseTimeoutError,
    ServerStopTimeoutError,
)

logger = Logger(__name__)


class Server:
    def __init__(self, server_settings: dict[str, str | int | list[str]]):
        needed_settings = [
            "java",
            "jar_name",
            "path",
            "key",
            "minecraft_version",
            "server_software",
        ]
        needed = [item for item in needed_settings if item not in server_settings]

        if needed:
            raise InvalidConfigError(
                f"Server configuration is missing values for: {', '.join(needed)}."
            )

        self._server_dir = Path(str(server_settings["path"]))

        if not self._server_dir.exists():
            raise ServerFolderDoesNotExistError("Server folder doesn't exist.")

        self._jar_path = self._server_dir / str(server_settings["jar_name"])

        if not self._jar_path.exists():
            raise ServerJarDoesNotExistError("Server jar file does not exist.")

        self._java = str(server_settings["java"])
        self.key = server_settings["key"]
        self._minecraft_version = server_settings["minecraft_version"]
        self._server_software = server_settings["server_software"]

        self._java_args: list[str] = server_settings.get("java_args", [])  # type: ignore
        self._jar_args: list[str] = server_settings.get("jar_args", ["nogui"])  # type: ignore

        server_stop_timeout = server_settings.get("server_stop_timeout")
        self._server_stop_timeout = (
            server_stop_timeout if isinstance(server_stop_timeout, int) else 60
        )

        self._process: Popen[str] | None = None
        self._status: str | None = None
        self._logs: deque[str] = deque(maxlen=1000)
        self._players: list[str] = []
        self._players_event: Event = Event()
        self._queue: Queue[str] = Queue()
        self._stop_event: Event = Event()
        self._start_time: datetime | None = None
        self._max_players: int | None = None
        self._uptime: str | None = None

    def start(self) -> None:
        if not self._process or self._process.poll() is not None:
            logger.info(f'Server with daemon key "{self.key}" is starting.')
            start_command = [
                self._java,
                *self._java_args,
                "-jar",
                str(self._jar_path.name),
                *self._jar_args,
            ]
            self._process = Popen(
                start_command,
                cwd=str(self._server_dir),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )

            Thread(target=self._reader, daemon=True).start()
            Thread(target=self._updater, daemon=True).start()

            self._status = "starting"
            self._start_time = datetime.now()
        else:
            logger.error(
                f'Cannot start server: server with daemon key "{self.key}" is already running.'
            )
            raise ServerIsAlreadyRunningError("Server is already running.")

    def _reader(self) -> None:
        if self._process is None:
            return

        while True:
            line: str | None = self._process.stdout.readline()  # type: ignore

            if not line:
                try:
                    if self._process:
                        self._process.wait(timeout=5)
                except Exception:
                    pass
                self._status = "stopped"
                self._start_time = None
                self._process = None
                self._stop_event.set()
                break

            if "players online: " in line:
                self._players = line.split("players online: ")[1].split()
                self._max_players = line.split("max of ")[1].split()[0]  # type: ignore
                self._players_event.set()
            else:
                self._logs.append(line)
                self._queue.put(line)
                if "Done (" in line and ')! For help, type "help"' in line:
                    self._status = "running"
                elif "Stopping the server" in line:
                    self._status = "stopping"
                    self._start_time = None

    def execute_command(self, command: str) -> None:
        if not self._process or self._process.poll() is not None:
            raise ServerIsNotRunningError("Сервер не запущен.")

        self._process.stdin.write(command + "\n")  # type: ignore
        self._process.stdin.flush()  # type: ignore

    def _updater(self) -> None:
        while self._process is not None:
            self._uptime = self.get_uptime()
            try:
                self._players = self.get_players() or []
            except ServerResponseTimeoutError, ServerIsNotRunningError:
                self._players = []
            self._status = self.status()
            time.sleep(1)

    def stop(self) -> None:
        self.execute_command("stop")

    def get_uptime(self) -> str:
        if not self._start_time:
            return "0:0:0:0"

        delta = datetime.now() - self._start_time
        total_seconds = int(delta.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{days}:{hours}:{minutes}:{seconds}"

    def restart(self) -> None:
        self._stop_event.clear()
        self.stop()

        if not self._stop_event.wait(timeout=self._server_stop_timeout):
            raise ServerStopTimeoutError(
                f"Server hasn't stopped for {self._server_stop_timeout} seconds."
            )

        self.start()

    def status(self) -> str | None:
        if self._process is None or self._process.poll() is not None:
            self._status = "stopped"

        return self._status

    def get_players(self) -> list[str] | None:
        if not self._process or self._process.poll() is not None:
            raise ServerIsNotRunningError("Server is not running.")

        self._players_event.clear()
        self.execute_command("list")

        if not self._players_event.wait(timeout=5):
            raise ServerResponseTimeoutError("Сервер не ответил на команду list.")

        return self._players

    def get_server_info(self) -> dict[str, str | list[str] | None | int]:
        return {
            "status": self._status,
            "players": self._players,
            "minecraft_version": self._minecraft_version,
            "server_software": self._server_software,
            "uptime": self._uptime,
            "max_players": self._max_players,
        }

    def get_logs(self) -> list[str]:
        return list(self._logs)

    def get_pending_logs(self) -> list[str]:
        logs = []

        while True:
            try:
                logs.append(self._queue.get_nowait())
            except Empty:
                break

        return logs
