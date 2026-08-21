from src.common.utils.logger import Logger
from src.daemon.server import Server
from src.daemon.services.file_service import FileService

logger = Logger(__name__)


class PropertiesService:
    def __init__(self, file_service: FileService) -> None:
        self.file_service = file_service

    def get_properties(self, server: Server) -> dict[str, str] | None:
        properties_file = self.file_service.get_file_item(server, "server.properties")
        if not properties_file or properties_file.content is None:
            return None

        properties: dict[str, str] = {}
        for line in properties_file.content.splitlines():
            if "#" != line[0]:
                key, value = line.split("=", 1)
                properties[key] = value.rstrip("\n")

        return properties

    def set_property(self, server: Server, property: str, new_value: str) -> bool:
        properties_file = self.file_service.get_file_item(server, "server.properties")
        if not properties_file or properties_file.content is None:
            return False

        properties = properties_file.content.splitlines()

        is_changed = False
        for i, line in enumerate(properties):
            if line.startswith(property + "="):
                properties[i] = property + "=" + new_value
                is_changed = True
                break

        if is_changed:
            logger.info(f'Property "{property}" updated: "{new_value}"')
            self.file_service.update_file(
                server, "server.properties", new_content="\n".join(properties)
            )

        return is_changed
