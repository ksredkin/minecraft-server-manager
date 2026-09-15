from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.daemon.exceptions.backup import (
    BackupNotFoundError,
    BackupPermissionError,
    BackupsFolderDoesNotExistError,
    BackupsFolderInServerFolderError,
    InvalidBackupError,
)
from src.daemon.exceptions.server import ServerFolderDoesNotExistError
from src.daemon.server import Server
from src.daemon.services.backup_service import BackupService

SERVER_SETTINGS: dict[str, str | list[str]] = {
    "java": "java",
    "jar_name": "server.jar",
    "key": "123-456-789",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
    "java_args": ["-Xmx4G"],
}


def make_server(path: Path) -> Server:
    path.mkdir()
    (path / "server.jar").touch()
    return Server({**SERVER_SETTINGS, "path": str(path)})


def test_get_backups_and_get_backup(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    first = backups_dir / "survival_2026-01-01.zip"
    second = backups_dir / "survival_2026-01-02.zip"
    unrelated = backups_dir / "creative_2026-01-01.zip"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    unrelated.write_bytes(b"other")
    service = BackupService(backups_dir)

    backups = service.get_backups(server)
    found = service.get_backup(server, first.name)

    assert [backup.name for backup in backups] == [first.name, second.name]
    assert found is not None
    assert found.path == first
    assert found.size == len(b"first")
    assert service.get_backup(server, unrelated.name) is None


def test_create_and_delete_backup(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    (server.server_dir / "world.txt").write_text("world")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    service = BackupService(backups_dir)

    backup = service.create(server)

    assert backup.name.startswith("survival_")
    assert backup.path == backups_dir / backup.name
    assert backup.path.exists()
    assert backup.size > 0

    service.delete_backup(server, backup.name)

    assert not backup.path.exists()


def test_restore_backup_replaces_server_files(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    (server.server_dir / "world.txt").write_text("old")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    service = BackupService(backups_dir)
    backup = service.create(server)
    (server.server_dir / "world.txt").write_text("changed")

    service.restore_backup(server, backup.name)

    assert (server.server_dir / "world.txt").read_text() == "old"
    assert not server.server_dir.with_name("survival_old").exists()


def test_handle_chunk_appends_bytes(tmp_path: Path) -> None:
    path = tmp_path / "backup.zip"
    service = BackupService(tmp_path)

    service.handle_chunk(path, b"first")
    service.handle_chunk(path, b" second")

    assert path.read_bytes() == b"first second"


def test_create_rejects_backups_inside_server_folder(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    service = BackupService(server.server_dir / "backups")

    with pytest.raises(BackupsFolderInServerFolderError):
        service.create(server)


def test_create_rejects_missing_folders(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    service = BackupService(tmp_path / "missing-backups")

    with pytest.raises(BackupsFolderDoesNotExistError):
        service.create(server)

    missing_server = MagicMock(server_dir=tmp_path / "missing-server")
    existing_backups = BackupService(tmp_path / "backups")
    existing_backups.backups_dir.mkdir()
    with pytest.raises(ServerFolderDoesNotExistError):
        existing_backups.create(missing_server)


def test_create_maps_permission_error(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    service = BackupService(backups_dir)

    with (
        patch(
            "src.daemon.services.backup_service.shutil.make_archive",
            side_effect=PermissionError,
        ),
        pytest.raises(BackupPermissionError),
    ):
        service.create(server)


def test_delete_missing_backup_raises_backup_not_found(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    service = BackupService(backups_dir)

    with pytest.raises(BackupNotFoundError):
        service.delete_backup(server, "missing.zip")


def test_restore_invalid_backup_rolls_back(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    (server.server_dir / "world.txt").write_text("old")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    backup = backups_dir / "survival_invalid.zip"
    backup.write_bytes(b"not an archive")
    service = BackupService(backups_dir)

    with pytest.raises(InvalidBackupError):
        service.restore_backup(server, backup.name)

    assert (server.server_dir / "world.txt").read_text() == "old"


def test_delete_permission_error_is_mapped(tmp_path: Path) -> None:
    server = make_server(tmp_path / "survival")
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    backup = backups_dir / "survival_backup.zip"
    backup.touch()
    service = BackupService(backups_dir)

    with (
        patch.object(Path, "unlink", side_effect=PermissionError),
        pytest.raises(BackupPermissionError),
    ):
        service.delete_backup(server, backup.name)
