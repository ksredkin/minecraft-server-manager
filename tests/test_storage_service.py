import shutil
from pathlib import Path
from unittest import mock
from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.common.enums import DaemonTaskKind
from src.daemon.exceptions.storage_service import (
    ReservationNotFoundError,
    StorageAccessError,
)
from src.daemon.services.storage_service import StorageService


def test_get_disk_free_space(tmp_path: Path) -> None:
    storage_service = StorageService()

    diskusage_mock = Mock()
    diskusage_mock.free = 600
    with mock.patch.object(shutil, "disk_usage", lambda x: diskusage_mock):
        assert storage_service.get_disk_free_space(tmp_path) == 600

    not_existing_path = tmp_path / "not_existing_folder"
    with mock.patch.object(shutil, "disk_usage", lambda x: diskusage_mock):
        assert storage_service.get_disk_free_space(not_existing_path) == 600

    with mock.patch.object(shutil, "disk_usage", side_effect=OSError):
        with pytest.raises(StorageAccessError):
            storage_service.get_disk_free_space(tmp_path)

def test_storage_service(tmp_path) -> None:
    storage_service = StorageService()

    assert storage_service.get_reserved() == 0

    with pytest.raises(ReservationNotFoundError):
        storage_service.is_complete(uuid4())
    with pytest.raises(ReservationNotFoundError):
        storage_service.get_progress(uuid4())

    server_key = uuid4()
    reservation_id = uuid4()

    diskusage_mock = Mock()
    diskusage_mock.free = 122
    with mock.patch.object(shutil, "disk_usage", lambda x: diskusage_mock):
        assert storage_service.reserve(tmp_path / "luckperms.jar", reservation_id, 100, server_key, DaemonTaskKind.PLUGINS, "Luckperms")

    assert storage_service.get_reserved() == 100
    assert not storage_service.is_complete(reservation_id)
    assert storage_service.get_progress(reservation_id) == 0.0

    storage_service.add_progress(reservation_id, 100)
    assert storage_service.is_complete(reservation_id)
    assert storage_service.get_progress(reservation_id) == 100

    diskusage_mock.free = 22
    with mock.patch.object(shutil, "disk_usage", lambda x: diskusage_mock):
        assert not storage_service.reserve(tmp_path / "123.jar", uuid4(), 100, server_key, DaemonTaskKind.PLUGINS, "123")

    backup_reservation_id = uuid4()
    with mock.patch.object(shutil, "disk_usage", lambda x: diskusage_mock):
        assert storage_service.reserve(tmp_path / "2026.zip", backup_reservation_id, 20, server_key, DaemonTaskKind.BACKUPS, "2026")

    result = storage_service.get_tasks(server_key)
    assert len(result["backups"]) + len(result["plugins"]) == 2

    storage_service.remove_reservation(reservation_id)
    storage_service.remove_reservation(backup_reservation_id)
    assert storage_service.get_tasks(server_key) == {"backups": {}, "plugins": {}}
