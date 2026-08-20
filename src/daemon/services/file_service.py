from pathlib import Path
from src.daemon.server import Server
from dataclasses import dataclass


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

    def get_folder_item(
        self, server: Server, folder_path: str | None = None
    ) -> FolderItem | None:
        folder = self._get_safe_path(server, folder_path)
        if not folder or not folder.exists():
            return None

        items: list[FileSystemItem] = []
        for item in folder.iterdir():
            if item.is_dir():
                items.append(FolderItem(item.name, item, []))
            elif item.is_file():
                items.append(FileItem(item.name, item, item.stat().st_size))

        return FolderItem(folder.name, folder, items)

    def get_file_item(self, server: Server, file_path: str) -> FileItem | None:
        file = self._get_safe_path(server, file_path)
        if not file or not file.is_file() or not file.exists():
            return None

        return FileItem(
            file.name, file, file.stat().st_size, file.read_text(encoding="utf-8")
        )

    def write_file(
        self, server: Server, file_path: str, content: str | None = None
    ) -> FileItem | None:
        file = self._get_safe_path(server, file_path)
        if not file or file.exists():
            return None

        file.write_text(content or "", encoding="utf-8")
        return FileItem(file.name, file, file.stat().st_size, content)

    def update_file(
        self,
        server: Server,
        file_path: str,
        new_path: str | None = None,
        new_content: str | None = None,
    ) -> FileItem | None:
        file = self._get_safe_path(server, file_path)
        new_file = self._get_safe_path(server, new_path)
        if (
            not file
            or not file.exists()
            or not file.is_file()
            or not new_file
            or new_file.exists()
        ):
            return None

        if new_content:
            file.write_text(new_content, encoding="utf-8")

        if new_path:
            try:
                file.rename(new_file)
            except Exception as e:
                return None

        return FileItem(
            file.name if new_path is None else new_file.name,
            file if new_path is None else new_file,
            file.stat().st_size if new_path is None else new_file.stat().st_size,
            file.read_text(encoding="utf-8") if not new_content else new_content,
        )

    def update_folder(
        self, server: Server, folder_path: str, new_path: str | None = None
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

        if new_folder:
            try:
                folder.move(new_folder)
            except Exception:
                return None

        items: list[FileSystemItem] = []
        if new_path is None:
            for item in folder.iterdir():
                if item.is_dir():
                    items.append(FolderItem(item.name, item, []))
                elif item.is_file():
                    items.append(FileItem(item.name, item, item.stat().st_size))
        else:
            for item in new_folder.iterdir():
                if item.is_dir():
                    items.append(FolderItem(item.name, item, []))
                elif item.is_file():
                    items.append(FileItem(item.name, item, item.stat().st_size))

        return FolderItem(
            folder.name if new_path is None else new_folder.name,
            folder if new_path is None else new_folder,
            items,
        )

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

        folder.mkdir()
        return FolderItem(folder.name, folder, [])

    def delete_item(self, server: Server, path: str) -> bool:
        safe_path = self._get_safe_path(server, path)
        if not safe_path or not safe_path.exists():
            return False

        try:
            if safe_path.is_dir():
                safe_path.rmdir()
            safe_path.unlink()
        except Exception:
            return False

        return True
