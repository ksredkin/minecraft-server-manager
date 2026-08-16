from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Queue
from subprocess import PIPE, Popen
from threading import Event, Thread

from src.common.utils.logger import Logger
from src.daemon.exceptions.server import ServerIsAlreadyRunningError

logger = Logger(__name__)


class Server:
    def __init__(self, server_settings: dict[str, str | int | list[str]]):
        if not server_settings:
            raise ValueError("Конфигурация сервера не может быть пустой.")

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
            raise ValueError(
                f"В конфигурации сервера не установлены значения: {', '.join(needed)}."
            )

        self.server_dir = Path(str(server_settings["path"]))

        if not self.server_dir.exists():
            raise FileNotFoundError("Папки сервера не существует.")

        self.jar_path = self.server_dir / str(server_settings["jar_name"])

        if not self.server_dir.exists():
            raise FileNotFoundError("Jar файла сервера не существует.")

        self.java = str(server_settings["java"])
        self.key = server_settings["key"]
        self.minecraft_version = server_settings["minecraft_version"]
        self.server_software = server_settings["server_software"]

        self.java_args: list[str] = server_settings.get("java_args", [])  # type: ignore
        self.jar_args: list[str] = server_settings.get("jar_args", ["nogui"])  # type: ignore
        self.server_stop_timeout = server_settings.get("server_stop_timeout", 60)

        self.process: Popen[str] | None = None
        self.status: str | None = None
        self.logs: deque[str] = deque(maxlen=1000)
        self.players: list[str] = []
        self.players_event: Event = Event()
        self.queue: Queue[str] = Queue()
        self.stop_event: Event = Event()
        self.start_time: datetime | None = None
        self.max_players: int | None = None

    def start(self) -> None:
        if not self.process or self.process.poll() is not None:
            logger.info(f'Server with daemon key "{self.key}" is starting.')
            start_command = [
                self.java,
                *self.java_args,
                "-jar",
                str(self.jar_path.name),
                *self.jar_args,
            ]
            self.process = Popen(
                start_command,
                cwd=str(self.server_dir),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )

            Thread(target=self._reader, daemon=True).start()

            self.status = "starting"
            self.start_time = datetime.now()
        else:
            logger.error(
                f'Cannot start server: server with daemon key "{self.key}" is already running.'
            )
            raise ServerIsAlreadyRunningError("Server is already running.")

    def _reader(self) -> None:
        if self.process is None:
            return

        while True:
            line: str | None = self.process.stdout.readline()  # type: ignore

            if not line:
                try:
                    if self.process:
                        self.process.wait(timeout=5)
                except Exception:
                    pass
                self.status = "stopped"
                self.start_time = None
                self.process = None
                self.stop_event.set()
                break

            self.logs.append(line)
            self.queue.put(line)

            if "players online: " in line:
                self.players = line.split("players online: ")[1].split()
                self.max_players = line.split("max of ")[1].split()[0]  # type: ignore
                self.players_event.set()
            elif "Done (" in line and ')! For help, type "help"' in line:
                self.status = "running"
            elif "Stopping the server" in line:
                self.status = "stopping"
                self.start_time = None

    # def stop(self) -> None:
    #    self.execute_command("stop")


"""
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
    
    def restart(self) -> bool:
        self._stop_event.clear()
        self.stop()
    
        if not self._stop_event.wait(timeout=SERVER_STOP_TIMEOUT):
            raise ServerStopTimeoutError(
                f"Сервер не остановился за {SERVER_STOP_TIMEOUT} секунд."
            )
    
        return self.start()
    
    def status(self) -> str | None:
        if self._process is None or self._process.poll() is not None:
            self._status = "stopped"
    
        return self._status
    
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
    
    def get_server_info(self) -> dict[str, str | list[str] | None | int]:
        if not self._process or self._process.poll() is not None:
            return {
                "status": "stopped",
                "minecraft_version": MINECRAFT_VERSION,
                "server_software": SERVER_SOFTWARE,
                "uptime": self.get_uptime(),
                "max_players": self._max_players,
            }
    
        try:
            players = self.get_players()
        except ServerResponseTimeoutError, ServerNotRunningError:
            players = None
    
        info = {
            "status": self.status(),
            "players": players,
            "minecraft_version": MINECRAFT_VERSION,
            "server_software": SERVER_SOFTWARE,
            "uptime": self.get_uptime(),
            "max_players": self._max_players,
        }
        return info
    
    def get_logs(self) -> list[str]:
        return list(self._logs)
"""
