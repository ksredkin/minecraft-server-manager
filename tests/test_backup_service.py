import shutil
from pathlib import Path
from shutil import make_archive
from typing import Any
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from src.api.exceptions.backups import (
    BackupNotFoundError,
    BackupPermisionError,
    BackupRestoreError,
    CleanupError,
    InvalidBackupError,
)
from src.api.exceptions.server import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
)
from src.api.services.backup_service import BackupService, get_backup_service


def test_invalid_server_configuration_(tmp_path: Any) -> None:
    with pytest.raises(InvalidServerConfigurationError):
        BackupService(server_path=None)  # type: ignore

    with pytest.raises(InvalidServerConfigurationError):
        BackupService(server_path=str(tmp_path), backups_path=None)  # type: ignore


def test_server_folder_does_not_exist() -> None:
    with pytest.raises(ServerFolderDoesNotExistError):
        BackupService(server_path="non_existent_folder")


def test_remove_archive(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    backup = backups_dir / "backup-08-07-2026-11-09.zip"

    assert not backup.exists()
    make_archive(str(backup).rstrip(".zip"), "zip", str(server_dir))
    assert backup.exists()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))
    service._remove_archive(backup)

    assert not backup.exists()


@freeze_time("2026-08-07 11:09:00")
def test_create_backup(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    assert service.create_backup() == "server_2026-08-07_11-09-00-000000.zip"
    assert (backups_dir / "server_2026-08-07_11-09-00-000000.zip").exists()


def test_delete_backup(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))
    backup = service.create_backup()

    assert (backups_dir / backup).exists()

    service.delete_backup(backup)

    assert not (backups_dir / backup).exists()


def test_get_backups(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))
    backup = service.create_backup()

    assert (backups_dir / backup).exists()
    assert service.get_backups() == [backup]


def test_check_backup_exists(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with pytest.raises(BackupNotFoundError):
        service._check_backup_exists(Path(":)"))

    backup = service.create_backup()
    assert service._check_backup_exists(backups_dir / backup) is None  # type: ignore


def test_cleanup(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    server_old_dir = tmp_dir / "server_old"

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with pytest.raises(CleanupError):
        service._cleanup("123")

    server_old_dir.mkdir()
    assert server_old_dir.exists()

    service._cleanup("123")
    assert not server_old_dir.exists()


def test_delete_server_dir(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()
    assert server_dir.exists()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    service._delete_server_dir()

    assert not server_dir.exists()


def test_rollback(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()
    assert server_dir.exists()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    server_old_dir = tmp_dir / "server_old"
    server_old_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    service._rollback()

    assert server_dir.exists()
    assert not server_old_dir.exists()


def test_delete_old_server_dir(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    server_old_dir = tmp_dir / "server_old"
    server_old_dir.mkdir()
    assert server_old_dir.exists()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))
    service._delete_old_server_dir()
    assert not server_old_dir.exists()


def test_restore_backup(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    server_properties = server_dir / "server.properties"

    with server_properties.open("w") as f:
        f.write("online-mode=false")

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    server_old_dir = tmp_dir / "server_old"
    server_old_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    backup = service.create_backup()

    with server_properties.open("w") as f:
        f.write("online-mode=true")

    service.restore_backup(backup)

    with server_properties.open("r") as f:
        assert f.read() == "online-mode=false"


def test_delete_backup_not_found(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with pytest.raises(BackupNotFoundError):
        service.delete_backup("missing_backup.zip")


def test_restore_backup_not_found(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with pytest.raises(BackupNotFoundError):
        service.restore_backup("missing_backup.zip")


def test_create_backup_permission_error(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with patch(
        "src.api.services.backup_service.shutil.make_archive",
        side_effect=PermissionError,
    ):
        with pytest.raises(BackupPermisionError):
            service.create_backup()

    assert service.get_backups() == []


def test_create_backup_restore_error(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with patch(
        "src.api.services.backup_service.shutil.make_archive",
        side_effect=OSError("boom"),
    ):
        with pytest.raises(BackupRestoreError):
            service.create_backup()

    assert service.get_backups() == []


def test_cleanup_error(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    server_old_dir = tmp_dir / "server_old"
    server_old_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    with patch(
        "src.api.services.backup_service.shutil.rmtree", side_effect=OSError("boom")
    ):
        with pytest.raises(CleanupError):
            service._cleanup("123")


def test_restore_backup_permission_error(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    backup = service.create_backup()

    with patch(
        "src.api.services.backup_service.shutil.unpack_archive",
        side_effect=PermissionError,
    ):
        with pytest.raises(BackupPermisionError):
            service.restore_backup(backup)


def test_restore_backup_invalid_backup_error(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))

    server_dir = tmp_dir / "server"
    server_dir.mkdir()

    backups_dir = tmp_dir / "backups"
    backups_dir.mkdir()

    service = BackupService(backups_path=str(backups_dir), server_path=str(server_dir))

    backup = service.create_backup()

    with patch(
        "src.api.services.backup_service.shutil.unpack_archive",
        side_effect=shutil.ReadError("bad"),
    ):
        with pytest.raises(InvalidBackupError):
            service.restore_backup(backup)


def test_get_backup_service() -> None:
    service1 = get_backup_service()
    service2 = get_backup_service()

    assert service1 is service2
