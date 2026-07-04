from pathlib import Path

from src.common.core.config import SERVER_PATH
from src.common.exceptions.server import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
)
from src.common.exceptions.settings import SettingsFileNotFoundError


class PropertiesService:
    def __init__(self, server_path: str = SERVER_PATH) -> None:
        if not server_path:
            raise InvalidServerConfigurationError(
                "В конфиге не установлен путь к серверу."
            )

        self.server_dir = Path(server_path)

        if not self.server_dir.exists():
            raise ServerFolderDoesNotExistError("Папки сервера не существует.")

        self.properties_file = self.server_dir / "server.properties"

    def get_properties(self) -> dict[str, str]:
        if not self.properties_file.exists():
            raise SettingsFileNotFoundError("Не найден файл настройки сервера.")

        with self.properties_file.open("r") as f:
            lines = f.readlines()

        properties = {}

        for line in lines:
            if "#" != line[0]:
                key, value = line.split("=", 1)
                properties[key] = value.rstrip("\n")

        return properties

    def update_property(self, property: str, value: str) -> None:
        if not self.properties_file.exists():
            raise SettingsFileNotFoundError("Не найден файл настройки сервера.")

        with self.properties_file.open("r") as f:
            properties = f.readlines()

        is_changed = False

        for i, line in enumerate(properties):
            if line.startswith(property + "="):
                properties[i] = property + "=" + value + "\n"
                is_changed = True
                break

        if is_changed:
            with self.properties_file.open("w") as f:
                f.writelines(properties)


properties_service = PropertiesService()


def get_properties_service() -> PropertiesService:
    return properties_service
