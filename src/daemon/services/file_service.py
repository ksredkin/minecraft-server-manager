from dataclasses import dataclass
from pathlib import Path

from src.common.utils.logger import Logger
from src.daemon.server import Server
from src.daemon.exceptions.file_service import (
    FileReadError,
    FileServiceError,
    FileWriteError,
    FolderReadError,
    FolderWriteError,
    InvalidPathError,
    ItemAlreadyExistsError,
    ItemDeleteError,
    ItemNotFoundError,
    ItemTypeError,
)
import shutil

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
    def _get_safe_path(self, server: Server, user_path: str | None) -> Path:
        server_dir = server.server_dir.resolve()

        if user_path is None:
            return server_dir

        target_file = (server.server_dir / user_path).resolve()

        if not target_file.is_relative_to(server_dir):
            raise InvalidPathError("Path is outside the server directory.")

        return target_file

    def _get_relative_path(self, server: Server, path: Path) -> Path:
        server_dir = server.server_dir.resolve()
        resolved_path = path.resolve()

        if not resolved_path.is_relative_to(server_dir):
            logger.warning(
                f"Path is outside the server directory: {str(resolved_path)}"
            )
            return resolved_path

        return Path(server_dir.name) / resolved_path.relative_to(server_dir)

    def get_folder_item(
        self, server: Server, folder_path: str | None = None
    ) -> FolderItem:
        folder = self._get_safe_path(server, folder_path)
        if not folder.exists():
            raise ItemNotFoundError("Folder not found.")
        if not folder.is_dir():
            raise ItemTypeError("Item is not a folder.")

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
            raise FolderReadError("Failed to read folder.") from e

    def get_file_item(self, server: Server, file_path: str) -> FileItem:
        file = self._get_safe_path(server, file_path)
        if not file.exists():
            raise ItemNotFoundError("File not found.")
        if not file.is_file():
            raise ItemTypeError("Item is not a file.")

        try:
            size = file.stat().st_size
            content = file.read_text(encoding="utf-8")

            return FileItem(file.name, file, size, content)
        except UnicodeDecodeError:
            return FileItem(file.name, file, size, None)
        except Exception as e:
            logger.error(f"Failed to get a file item: {e}")
            raise FileReadError("Failed to read file.") from e

    def write_file(
        self, server: Server, file_path: str, content: str | None = None
    ) -> FileItem:
        file = self._get_safe_path(server, file_path)
        if file.exists():
            raise ItemAlreadyExistsError("File already exists.")

        try:
            file.write_text(content if content is not None else "", encoding="utf-8")
            size = file.stat().st_size
            logger.info(
                f"Created file at: {str(self._get_relative_path(server, file))}"
            )
            return FileItem(file.name, file, size, content)
        except Exception as e:
            logger.error(f"Failed to create a new file: {e}", exc_info=True)
            raise FileWriteError("Failed to create file.") from e

    def update_file(
        self,
        server: Server,
        file_path: str,
        new_path: str | None = None,
        new_content: str | None = None,
    ) -> FileItem:
        file = self._get_safe_path(server, file_path)

        if not file.exists():
            raise ItemNotFoundError("File not found.")
        if not file.is_file():
            raise ItemTypeError("Item is not a file.")

        new_file = None
        if new_path is not None:
            new_file = self._get_safe_path(server, new_path)
            if new_file.exists():
                raise ItemAlreadyExistsError("File already exists.")

        try:
            name = file.name
            path = file
            size = file.stat().st_size
            content = file.read_text(encoding="utf-8")

            if new_content is not None:
                file.write_text(new_content, encoding="utf-8")
                content = new_content
                size = file.stat().st_size

            if new_file:
                file.rename(new_file)
                name = new_file.name
                path = new_file

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
            if isinstance(e, FileServiceError):
                raise
            raise FileWriteError("Failed to update file.") from e

    def update_folder(
        self, server: Server, folder_path: str, new_path: str
    ) -> FolderItem:
        folder = self._get_safe_path(server, folder_path)
        new_folder = self._get_safe_path(server, new_path)
        if not folder.exists():
            raise ItemNotFoundError("Folder not found.")
        if not folder.is_dir():
            raise ItemTypeError("Item is not a folder.")
        if new_folder.exists():
            raise ItemAlreadyExistsError("Folder already exists.")

        try:
            folder.rename(new_folder)

            items: list[FileSystemItem] = []
            for item in new_folder.iterdir():
                    if item.is_dir():
                        items.append(FolderItem(item.name, item, []))
                    elif item.is_file():
                        size = item.stat().st_size
                        items.append(FileItem(item.name, item, size))

            logger.info(
                f"Updated folder at: {str(self._get_relative_path(server, new_folder))}"
            )

            return FolderItem(
                new_folder.name,
                new_folder,
                items,
            )
        except Exception as e:
            logger.error(f"Failed to update a folder: {e}", exc_info=True)
            raise FolderWriteError("Failed to update folder.") from e

    def get_item(
        self, server: Server, item_path: str | None = None
    ) -> FileSystemItem:
        item = self._get_safe_path(server, item_path)
        if not item.exists():
            raise ItemNotFoundError("Item not found.")

        if item.is_dir():
            return self.get_folder_item(server, item_path)

        if item.is_file():
            if item_path is None:
                raise ItemTypeError("A file path is required.")
            return self.get_file_item(server, item_path)

        raise ItemTypeError("Unsupported filesystem item.")

    def create_folder(
        self, server: Server, folder_path: str | None = None
    ) -> FolderItem:
        folder = self._get_safe_path(server, folder_path)
        if folder.exists():
            raise ItemAlreadyExistsError("Folder already exists.")

        try:
            folder.mkdir()
            logger.info(
                f"Created folder at: {str(self._get_relative_path(server, folder))}"
            )
            return FolderItem(folder.name, folder, [])
        except Exception as e:
            logger.error(f"Failed to create a folder: {e}", exc_info=True)
            raise FolderWriteError("Failed to create folder.") from e

    def delete_item(self, server: Server, path: str) -> None:
        safe_path = self._get_safe_path(server, path)
        if not safe_path.exists():
            raise ItemNotFoundError("Item not found.")

        try:
            if safe_path.is_dir():
                shutil.rmtree(safe_path)
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
            raise ItemDeleteError("Failed to delete item.") from e
