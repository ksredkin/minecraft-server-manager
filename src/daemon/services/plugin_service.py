from dataclasses import dataclass
from pathlib import Path

from src.common.utils.logger import Logger
from src.daemon.exceptions.plugin import (
    PluginNotFoundError,
    PluginsFolderDoesNotExistError,
)
from src.daemon.server import Server
from src.daemon.services.file_service import FileItem, FileService, FolderItem

logger = Logger(__name__)


@dataclass
class Plugin:
    name: str
    path: Path
    size: int


class PluginService:
    def __init__(self, file_service: FileService) -> None:
        self.file_service = file_service

    def _get_plugins_folder_item(self, server: Server) -> FolderItem:
        plugins_folder = self.file_service.get_folder_item(server, "plugins")
        if not plugins_folder:
            logger.error(f'Plugins folder of server "{server.key}" doesn\'t exist.')
            raise PluginsFolderDoesNotExistError("Plugins folder doesn't exist.")
        return plugins_folder

    def get_plugins(self, server: Server) -> list[Plugin]:
        plugins_folder = self._get_plugins_folder_item(server)

        ret = []
        for item in plugins_folder.items:
            if isinstance(item, FileItem) and item.name.endswith(".jar"):
                ret.append(Plugin(item.path.stem.capitalize(), item.path, item.size))

        return ret

    def delete(self, server: Server, plugin: str) -> None:
        if not plugin.endswith(".jar"):
            raise PluginNotFoundError("Plugin not found.")
        file = server.server_dir / "plugins" / plugin
        deleted = self.file_service.delete_item(server, str(file))
        if not deleted:
            raise PluginNotFoundError("Plugin not found.")

    def handle_chunk(self, path: Path, chunk: bytes) -> None:
        with path.open("ab") as f:
            f.write(chunk)
