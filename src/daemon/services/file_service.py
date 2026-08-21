from dataclasses import dataclass
from pathlib import Path

from src.common.utils.logger import Logger
from src.daemon.server import Server

logger = Logger(__name__)


@dataclass
class FileSystemItem:
    name: str
    path: Path


@dataclass
class FileItem(FileSystemItem):
    size: int
    content: str | None = None


@dataclass
class FolderItem(FileSystemItem):
    items: list[FileSystemItem]


class FileService:
    def get_path(self, server: Server, user_path: str | None) -> Path:
        server_dir = server.server_dir.resolve()

        if user_path is None:
            return server_dir

        return (server.server_dir / user_path).resolve()

    def _get_safe_path(self, server: Server, user_path: str | None) -> Path | None:
        server_dir = server.server_dir.resolve()

        if user_path is None:
            return server_dir

        target_file = (server.server_dir / user_path).resolve()

        if not target_file.is_relative_to(server_dir):
            return None

        return target_file

    def _get_relative_path(self, server: Server, path: Path) -> Path:
        return Path(server.server_dir.name) / path.relative_to(server.server_dir)

    def get_folder_item(
        self, server: Server, folder_path: str | None = None
    ) -> FolderItem | None:
        folder = self._get_safe_path(server, folder_path)
        if not folder or not folder.exists() or not folder.is_dir():
            return None

        try:
            items: list[FileSystemItem] = []
            for item in folder.iterdir():
                if item.is_dir():
                    items.append(FolderItem(item.name, item, []))
                elif item.is_file():
                    size = item.stat().st_size
                    items.append(FileItem(item.name, item, size))

            return FolderItem(folder.name, folder, items)
        except Exception as e:
            logger.error(f"Failed to get a folder item: {e}", exc_info=True)
            return None

    def get_file_item(self, server: Server, file_path: str) -> FileItem | None:
        file = self._get_safe_path(server, file_path)
        if not file or not file.exists() or not file.is_file():
            return None

        try:
            size = file.stat().st_size
            content = file.read_text(encoding="utf-8")

            return FileItem(file.name, file, size, content)
        except Exception as e:
            logger.error(f"Failed to get a file item: {e}", exc_info=True)
            return None

    def write_file(
        self, server: Server, file_path: str, content: str | None = None
    ) -> FileItem | None:
        file = self._get_safe_path(server, file_path)
        if not file or file.exists():
            return None

        try:
            file.write_text(content if content is not None else "", encoding="utf-8")
            size = file.stat().st_size
            logger.info(
                f"Created file at: {str(self._get_relative_path(server, file))}"
            )
            return FileItem(file.name, file, size, content)
        except Exception as e:
            logger.error(f"Failed to create a new file: {e}", exc_info=True)
            return None

    def update_file(
        self,
        server: Server,
        file_path: str,
        new_path: str | None = None,
        new_content: str | None = None,
    ) -> FileItem | None:
        file = self._get_safe_path(server, file_path)

        if not file or not file.exists() or not file.is_file():
            return None

        new_file = None
        if new_path is not None:
            new_file = self._get_safe_path(server, new_path)
            if not new_file or new_file.exists():
                return None

        try:
            if new_content is not None:
                file.write_text(new_content, encoding="utf-8")

            if new_file:
                file.rename(new_file)

            name = file.name if new_file is None else new_file.name
            path = file if new_file is None else new_file
            size = file.stat().st_size if new_file is None else new_file.stat().st_size
            content = (
                file.read_text(encoding="utf-8") if not new_content else new_content
            )

            logger.info(
                f"Updated file at: {str(self._get_relative_path(server, path))}"
            )

            return FileItem(
                name,
                path,
                size,
                content,
            )
        except Exception as e:
            logger.error(f"Failed to update a file: {e}", exc_info=True)
            return None

    def update_folder(
        self, server: Server, folder_path: str, new_path: str
    ) -> FolderItem | None:
        folder = self._get_safe_path(server, folder_path)
        new_folder = self._get_safe_path(server, new_path)
        if (
            not folder
            or not folder.exists()
            or not folder.is_dir()
            or not new_folder
            or new_folder.exists()
        ):
            return None

        try:
            if new_folder:
                folder.rename(new_folder)

            items: list[FileSystemItem] = []
            if new_path is None:
                for item in folder.iterdir():
                    if item.is_dir():
                        items.append(FolderItem(item.name, item, []))
                    elif item.is_file():
                        size = item.stat().st_size
                        items.append(FileItem(item.name, item, size))
            else:
                for item in new_folder.iterdir():
                    if item.is_dir():
                        items.append(FolderItem(item.name, item, []))
                    elif item.is_file():
                        size = item.stat().st_size
                        items.append(FileItem(item.name, item, size))

            logger.info(
                f"Updated folder at: {str(self._get_relative_path(server, folder if new_path is None else new_folder))}"
            )

            return FolderItem(
                folder.name if new_path is None else new_folder.name,
                folder if new_path is None else new_folder,
                items,
            )
        except Exception as e:
            logger.error(f"Failed to update a folder: {e}", exc_info=True)
            return None

    def get_item(
        self, server: Server, item_path: str | None = None
    ) -> FileSystemItem | None:
        item = self._get_safe_path(server, item_path)
        if not item or not item.exists():
            return None

        if item.is_dir():
            return self.get_folder_item(server, item_path)

        if item.is_file():
            if item_path:
                return self.get_file_item(server, item_path)

        return None

    def create_folder(
        self, server: Server, folder_path: str | None = None
    ) -> FolderItem | None:
        folder = self._get_safe_path(server, folder_path)
        if not folder or folder.exists():
            return None

        try:
            folder.mkdir()
            logger.info(
                f"Created folder at: {str(self._get_relative_path(server, folder))}"
            )
            return FolderItem(folder.name, folder, [])
        except Exception as e:
            logger.error(f"Failed to create a folder: {e}", exc_info=True)
            return None

    def delete_item(self, server: Server, path: str) -> bool:
        safe_path = self._get_safe_path(server, path)
        if not safe_path or not safe_path.exists():
            return False

        try:
            if safe_path.is_dir():
                safe_path.rmdir()
                logger.info(
                    f"Deleted folder at: {str(self._get_relative_path(server, safe_path))}"
                )
            else:
                safe_path.unlink()
                logger.info(
                    f"Deleted file at: {str(self._get_relative_path(server, safe_path))}"
                )
        except Exception as e:
            logger.error(f"Failed to delete a file: {e}", exc_info=True)
            return False

        return True
