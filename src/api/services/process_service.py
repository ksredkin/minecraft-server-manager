from pathlib import Path
from subprocess import PIPE, Popen

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

    def start(self) -> bool:
        if not self._process or self._process.poll() is not None:
            if not self.server_dir.exists():
                raise RuntimeError("Папки сервера не существует.")

            if not JAVA:
                raise ValueError("В конфиге не указана java.")

            if not JAR_NAME:
                raise ValueError("В конфиге не указано имя jar файла.")

            start_command = [JAVA, *JAVA_ARGS, "-jar", JAR_NAME, *JAR_ARGS]
            self._process = Popen(start_command, cwd=SERVER_PATH, stdin=PIPE, text=True)

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


process_service = ProcessService()


def get_process_service() -> ProcessService:
    return process_service
