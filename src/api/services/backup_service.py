import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.common.core.config import BACKUPS_PATH, SERVER_PATH
from src.common.exceptions import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
)


class BackupService:
    def __init__(
        self, backups_path: str = BACKUPS_PATH, server_path: str = SERVER_PATH
    ) -> None:
        if not server_path:
            raise InvalidServerConfigurationError(
                "В конфиге не установлен путь к серверу."
            )

        server_dir = Path(server_path)

        if not server_dir.exists():
            raise ServerFolderDoesNotExistError("Папки сервера не существует.")

        self.server_dir = server_dir

        if not backups_path:
            raise InvalidServerConfigurationError(
                "В конфиге не установлен путь к папке бэкапов."
            )

        backups_dir = Path(backups_path)

        if not backups_dir.exists():
            backups_dir.mkdir(exist_ok=True, parents=True)

        self.backups_dir = backups_dir

    def create_backup(self) -> str:
        current_date_and_time = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d_%H-%M-%S-%f"
        )
        server_folder_name = self.server_dir.name

        archive_name = f"{server_folder_name}_{current_date_and_time}"
        archive_path = self.backups_dir / archive_name

        shutil.make_archive(str(archive_path), "zip", str(self.server_dir))

        return f"{archive_name}.zip"

    def get_backups(self) -> list[str]:
        return [f.name for f in self.backups_dir.glob("*.zip")]


backup_service = BackupService()


def get_backup_service() -> BackupService:
    return backup_service
