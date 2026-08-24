from src.common.utils.logger import Logger
from src.daemon.server import Server
from pathlib import Path
from src.daemon.exceptions.backup import (
    BackupsFolderInServerFolderError,
    BackupsFolderDoesNotExistError,
    BackupRestoreError,
    BackupPermissionError,
    BackupNotFoundError,
    InvalidBackupError,
    CleanupError,
)
from src.daemon.exceptions.server import ServerFolderDoesNotExistError
from dataclasses import dataclass
import shutil
from datetime import datetime, timezone

logger = Logger(__name__)


@dataclass
class Backup:
    name: str
    path: Path
    size: int


class BackupService:
    def __init__(self, backups_dir: Path) -> None:
        self.backups_dir = backups_dir

    def _get_relative_path(self, server: Server, path: Path) -> Path:
        return Path(server.server_dir.name) / path.relative_to(server.server_dir)

    def get_backups(self, server: Server) -> list[Backup]:
        if not self.backups_dir.exists():
            raise BackupsFolderDoesNotExistError("Backups folder does not exist.")

        return [
            Backup(item.name, item, item.stat().st_size)
            for item in self.backups_dir.glob("*.zip")
            if server.server_dir.name in item.name
        ]

    def _check_backup_exists(self, backup: Path) -> None:
        if not backup.exists():
            logger.error(f'Backup "{backup.name}" not found.')
            raise BackupNotFoundError(f'Backup "{backup.name}" not found.')

    def _remove_archive(self, path: Path) -> None:
        if path.exists():
            path.unlink()

    def _delete_server_dir(self, server_dir: Path) -> None:
        if server_dir.exists():
            shutil.rmtree(server_dir)

    def _rollback(self, server_old_dir: Path, server_dir: Path) -> None:
        if server_old_dir.exists():
            self._delete_server_dir()
            server_old_dir.rename(server_dir)

    def _delete_old_server_dir(self, server_old_dir: Path) -> None:
        if server_old_dir.exists():
            shutil.rmtree(server_old_dir)

    def _cleanup(self, server_old_dir: Path, backup: str) -> None:
        try:
            shutil.rmtree(str(server_old_dir))
        except OSError:
            raise CleanupError(
                f'Cannot delete a temp folder, but restoring "{backup}" went successful.'
            )

    def create(self, server: Server) -> Backup:
        if self.backups_dir.is_relative_to(server.server_dir):
            raise BackupsFolderInServerFolderError(
                "Backups folder is in server folder."
            )

        if not self.backups_dir.exists():
            raise BackupsFolderDoesNotExistError("Backups folder does not exist.")

        if not server.server_dir.exists():
            raise ServerFolderDoesNotExistError("Server folder does not exist.")

        current_date_and_time = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d_%H-%M-%S-%f"
        )
        server_folder_name = server.server_dir.name

        archive_name = f"{server_folder_name}_{current_date_and_time}"
        archive_path = self.backups_dir / archive_name

        try:
            shutil.make_archive(
                str(archive_path), "zip", base_dir=str(server.server_dir)
            )
        except PermissionError:
            self._remove_archive(archive_path.with_suffix(".zip"))
            logger.error(
                f'Permission denied: cannot create backup "{archive_name}.zip".'
            )
            raise BackupPermissionError(
                f'Permission denied: cannot create backup "{archive_name}.zip".'
            )
        except OSError as e:
            logger.error(
                f'Cannot create backup "{archive_name}.zip": {e}', exc_info=True
            )
            self._remove_archive(archive_path.with_suffix(".zip"))
            raise BackupRestoreError(str(e))
        except Exception as e:
            logger.error(
                f'Cannot create backup "{archive_name}.zip": {e}', exc_info=True
            )
            self._remove_archive(archive_path.with_suffix(".zip"))
            raise e

        logger.info(f'Created backup: "{archive_name}.zip"')
        return Backup(
            archive_name,
            archive_path.with_suffix(".zip"),
            archive_path.with_suffix(".zip").stat().st_size,
        )

    def delete_backup(self, server: Server, backup_name: str) -> None:
        if self.backups_dir.is_relative_to(server.server_dir):
            raise BackupsFolderInServerFolderError(
                "Backups folder is in server folder."
            )

        if not self.backups_dir.exists():
            raise BackupsFolderDoesNotExistError("Backups folder does not exist.")

        if not server.server_dir.exists():
            raise ServerFolderDoesNotExistError("Server folder does not exist.")

        found = False
        for backup in self.backups_dir.glob("*.zip"):
            if backup.name == backup_name and server.server_dir.name in backup.name:
                found = True

        if not found:
            logger.error(f'Backup "{backup.name}" not found or access denied.')
            raise BackupNotFoundError(
                f'Backup "{backup.name}" not found or access denied.'
            )

        backup_path = self.backups_dir / backup_name

        try:
            backup_path.unlink()
        except PermissionError:
            logger.error(
                f'Permission denied: cannot create backup "{backup_name}.zip".'
            )
            raise BackupPermissionError(
                f'Permission denied: cannot create backup "{backup_name}.zip".'
            )
        except OSError as e:
            logger.error(
                f'Cannot create backup "{backup_name}.zip": {e}', exc_info=True
            )
            raise BackupRestoreError(str(e))
        except Exception as e:
            logger.error(
                f'Cannot create backup "{backup_name}.zip": {e}', exc_info=True
            )
            raise e

    def restore_backup(self, server: Server, backup_name: str) -> None:
        backup_path = self.backups_dir / backup_name

        found = False
        for backup in self.backups_dir.glob("*.zip"):
            if backup.name == backup_name and server.server_dir.name in backup.name:
                found = True

        if not found:
            logger.error(f'Backup "{backup.name}" not found or access denied.')
            raise BackupNotFoundError(
                f'Backup "{backup.name}" not found or access denied.'
            )

        server_old_dir = server.server_dir.with_name(f"{server.server_dir.name}_old")

        self._delete_old_server_dir(server_old_dir)
        server.server_dir.rename(server_old_dir)

        try:
            try:
                shutil.unpack_archive(str(backup_path), str(server.server_dir.parent))
                logger.info(f'Backup "{backup.name}" successfully restored.')
            except Exception:
                self._rollback()
                raise
        except FileNotFoundError:
            logger.error(f'Cannot restore backup "{backup.name}": not found.')
            raise BackupNotFoundError(f'Backup "{backup.name}" not found.')
        except shutil.ReadError:
            logger.error(
                f'Cannot restore backup "{backup_name}": the backup is invalid.'
            )
            raise InvalidBackupError(f'Backup "{backup_name}" is invalid.')
        except PermissionError:
            logger.error(
                f'Permission denied: cannot restore backup "{backup_name}.zip."'
            )
            raise BackupPermissionError(
                f'Permission denied: cannot restore backup "{backup_name}.zip."'
            )
        except OSError as e:
            logger.error(f'Cannot restore backup "{backup.name}": {e}')
            raise BackupRestoreError(str(e))
        except Exception as e:
            logger.error(f'Cannot restore backup "{backup.name}": {e}')
            raise e

        self._cleanup(server_old_dir, backup_name)
