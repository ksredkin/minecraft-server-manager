from pathlib import Path

from src.common.core.config import SERVER_PATH


class EulaService:
    def __init__(self, server_path: str = SERVER_PATH) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")

        server_dir = Path(server_path)

        if not server_dir.exists():
            raise RuntimeError("Папки сервера не существует.")

        self.eula_file = server_dir / "eula.txt"

    def set_eula_status(self, accepted: bool) -> bool:
        if not self.eula_file.exists():
            raise ValueError("Файл eula.txt не найден.")

        with self.eula_file.open("r") as f:
            lines = f.readlines()

        is_changed = False

        for i, line in enumerate(lines):
            if line.startswith("eula="):
                if accepted:
                    lines[i] = "eula=true\n"
                else:
                    lines[i] = "eula=false\n"
                is_changed = True

        if is_changed:
            with self.eula_file.open("w") as f:
                f.writelines(lines)

        return is_changed

    def get_eula_status(self) -> bool | None:
        if not self.eula_file.exists():
            raise ValueError("Файл eula.txt не найден.")

        with self.eula_file.open("r") as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith("eula="):
                return line.strip("=")[1].rstrip() == "true"

        return None


eula_service = EulaService()


def get_eula_service() -> EulaService:
    return eula_service
