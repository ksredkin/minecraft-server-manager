from src.common.core.config import SERVER_PATH
import os

class PropertiesService:
    def __init__(self, server_path: str = SERVER_PATH) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")
        
        properties_file_path = SERVER_PATH.rstrip("/").rstrip("\\") + "/" + "server.properties"

        if not os.path.exists(properties_file_path):
            raise RuntimeError("Не найден файл настройки сервера.")

        self.properties_file_path = properties_file_path

    def get_properties(self) -> dict[str, str]:
        with open(self.properties_file_path, "r") as f:
            lines = f.readlines()

        properties = {}

        for line in lines:
            if "#" != line[0]:
                key, value = line.split("=", 1)
                properties[key] = value.rstrip("\n")

        return properties

    def update_property(self, property: str, value: str) -> bool:
        with open(self.properties_file_path, "r") as f:
            properties = f.readlines()

        is_changed = False

        for i, line in enumerate(properties):
            if line.startswith(property + "="):
                properties[i] = property + "=" + value  + "\n"
                is_changed = True
                break

        if is_changed:
            with open(self.properties_file_path, "w") as f:
                f.writelines(properties)

        return is_changed
