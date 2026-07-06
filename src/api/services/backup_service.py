import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.common.core.config import BACKUPS_PATH, SERVER_PATH
from src.common.exceptions.backups import (
    BackupNotFoundError,
    BackupPermisionError,
    BackupRestoreError,
    CleanupError,
    InvalidBackupError,
)
from src.common.exceptions.server import (
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
        self.server_old_dir = server_dir.with_name(f"{server_dir.name}_old")

        if not backups_path:
            raise InvalidServerConfigurationError(
                "В конфиге не установлен путь к папке бэкапов."
            )

        backups_dir = Path(backups_path)

        if not backups_dir.exists():
            backups_dir.mkdir(exist_ok=True, parents=True)

        self.backups_dir = backups_dir

    def _remove_archive(self, path: Path) -> None:
        if path.exists():
            path.unlink()

    def create_backup(self) -> str:
        current_date_and_time = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d_%H-%M-%S-%f"
        )
        server_folder_name = self.server_dir.name

        archive_name = f"{server_folder_name}_{current_date_and_time}"
        archive_path = self.backups_dir / archive_name

        try:
            shutil.make_archive(str(archive_path), "zip", str(self.server_dir))
        except PermissionError:
            self._remove_archive(archive_path)
            raise BackupPermisionError(
                f"Не хватает прав для создания резервной копии {archive_name}.zip."
            )
        except OSError as e:
            self._remove_archive(archive_path)
            raise BackupRestoreError(str(e))
        except Exception:
            self._remove_archive(archive_path)
            raise

        return f"{archive_name}.zip"

    def delete_backup(self, backup_name: str) -> None:
        backup_path = self.backups_dir / backup_name
        self._check_backup_exists(backup_path)

        try:
            backup_path.unlink()
        except PermissionError:
            raise BackupPermisionError(
                f"Не хватает прав для удаления резервной копии {backup_name}."
            )
        except OSError as e:
            raise BackupRestoreError(str(e))
        except Exception:
            raise

    def get_backups(self) -> list[str]:
        return [f.name for f in self.backups_dir.glob("*.zip")]

    def _check_backup_exists(self, backup: Path) -> None:
        if not backup.exists():
            raise BackupNotFoundError(f"Резервная копия {backup.name} не найдена.")

    def _cleanup(self, backup: str) -> None:
        try:
            shutil.rmtree(str(self.server_old_dir))
        except OSError:
            raise CleanupError(
                f"Не удалось удалить временную папку server_old, но откат к резервной копии {backup} прошел успешно."
            )

    def _delete_server_dir(self) -> None:
        if self.server_dir.exists():
            shutil.rmtree(self.server_dir)

    def _rollback(self) -> None:
        if self.server_old_dir.exists():
            self._delete_server_dir()
            self.server_old_dir.rename(self.server_dir)

    def _delete_old_server_dir(self) -> None:
        if self.server_old_dir.exists():
            shutil.rmtree(self.server_old_dir)

    def restore_backup(self, backup_name: str) -> None:
        backup_path = self.backups_dir / backup_name

        self._check_backup_exists(backup_path)
        self._delete_old_server_dir()
        self.server_dir.rename(self.server_old_dir)
        self.server_dir.mkdir(parents=True, exist_ok=True)

        try:
            try:
                shutil.unpack_archive(str(backup_path), str(self.server_dir))
            except Exception:
                self._rollback()
                raise
        except FileNotFoundError:
            raise BackupNotFoundError(f"Резервная копия {backup_name} не найдена.")
        except shutil.ReadError:
            raise InvalidBackupError(f"Резервная копия {backup_name} повреждена.")
        except PermissionError:
            raise BackupPermisionError(
                f"Не хватает прав для восстановления из резервной копии {backup_name}."
            )
        except OSError as e:
            raise BackupRestoreError(str(e))
        except Exception:
            raise

        self._cleanup(backup_name)


backup_service = BackupService()


def get_backup_service() -> BackupService:
    return backup_service
