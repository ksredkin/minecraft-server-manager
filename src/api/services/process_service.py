from collections import deque
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread

from src.common.core.config import JAR_ARGS, JAR_NAME, JAVA, JAVA_ARGS, SERVER_PATH


class ProcessService:
    def __init__(self, server_path: str = SERVER_PATH):
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")

        self.server_dir = Path(server_path)

        if not self.server_dir.exists():
            raise RuntimeError("Папки сервера не существует.")

        self._process: Popen[str] | None = None
        self._status = None
        self._logs: deque[str] = deque(maxlen=1000)

    def start(self) -> bool:
        if not self._process or self._process.poll() is not None:
            if not self.server_dir.exists():
                raise RuntimeError("Папки сервера не существует.")

            if not JAVA:
                raise ValueError("В конфиге не указана java.")

            if not JAR_NAME:
                raise ValueError("В конфиге не указано имя jar файла.")

            start_command = [JAVA, *JAVA_ARGS, "-jar", JAR_NAME, *JAR_ARGS]
            self._process = Popen(
                start_command, cwd=SERVER_PATH, stdin=PIPE, stdout=PIPE, text=True
            )

            Thread(target=self._reader, daemon=True).start()

            return True
        return False

    def stop(self) -> bool:
        return self.execute_command("stop")

    def restart(self) -> bool:
        self.stop()
        self.start()
        return True

    def status(self) -> str:
        if self._process is None:
            return "stopped"

        if self._process.poll() is None:
            return "running"

        return "stopped"

    def execute_command(self, command: str) -> bool:
        if not self._process or self._process.poll() is not None:
            return False

        self._process.stdin.write(command + "\n")  # type: ignore
        self._process.stdin.flush()  # type: ignore

        return True

    def _reader(self) -> None:
        process = self._process

        if process is None:
            return

        while True:
            line = process.stdout.readline()  # type: ignore

            if not line:
                break

            self._logs.append(line)

    def get_logs(self) -> list[str]:
        return list(self._logs)


process_service = ProcessService()


def get_process_service() -> ProcessService:
    return process_service
