from src.common.utils.logger import Logger
from src.daemon.exceptions.file_service import (
    FileReadError,
    ItemNotFoundError,
    ItemTypeError,
)
from src.daemon.exceptions.properties_service import (
    InvalidPropertiesFileError,
    PropertiesFileNotFoundError,
    PropertiesFileReadError,
    PropertiesFileTypeError,
)
from src.daemon.server import Server
from src.daemon.services.file_service import FileItem, FileService

logger = Logger(__name__)


class PropertiesService:
    def __init__(self, file_service: FileService) -> None:
        self.file_service = file_service

    def _get_properties_file(self, server: Server) -> FileItem:
        try:
            properties_file = self.file_service.get_file_item(
                server, "server.properties"
            )
        except ItemNotFoundError:
            raise PropertiesFileNotFoundError("Properties file not found.")
        except ItemTypeError:
            raise PropertiesFileTypeError("Properties file has an invalid type.")
        except FileReadError as e:
            raise PropertiesFileReadError(
                "Properties file cannot be read as text."
            ) from e

        if not properties_file.content:
            raise InvalidPropertiesFileError("Properties file is empty.")

        return properties_file

    def get_properties(self, server: Server) -> dict[str, str]:
        properties_file = self._get_properties_file(server)

        properties: dict[str, str] = {}
        for line in properties_file.content.splitlines():  # type: ignore
            if "#" != line[0]:
                key, value = line.split("=", 1)
                properties[key] = value.rstrip("\n")

        return properties

    def set_property(self, server: Server, property: str, new_value: str) -> bool:
        properties_file = self._get_properties_file(server)
        lines = properties_file.content.splitlines()  # type: ignore

        target_line = f"{property}={new_value}"

        new_lines = []
        is_changed = False

        for line in lines:
            if line.startswith(property + "="):
                if line == target_line:
                    return True
                new_lines.append(property + "=" + new_value)
                is_changed = True
            else:
                new_lines.append(line)

        if not is_changed:
            return True

        logger.info(f'Property "{property}" updated: "{new_value}".')
        self.file_service.update_file(
            server, "server.properties", new_content="\n".join(new_lines)
        )
        return True
