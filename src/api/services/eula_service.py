from src.common.core.config import SERVER_PATH
import os

class EulaService:
    def __init__(self, server_path: str = SERVER_PATH) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")

        self.eula_file_path = SERVER_PATH.rstrip("/").rstrip("\\") + "/" + "eula.txt"

    def set_eula_status(self, accepted: bool) -> bool:
        if not os.path.exists(self.eula_file_path):
            raise RuntimeError("Не найден файл eula.")

        with open(self.eula_file_path, "r") as f:
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
            with open(self.eula_file_path, "w") as f:
                f.writelines(lines)

        return is_changed
