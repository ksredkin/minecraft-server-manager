from pathlib import Path

import pytest

from src.daemon.exceptions.eula_service import (
    EulaFileNotFoundError,
    InvalidEulaFileError,
    EulaFileUpdateError,
    InvalidEulaFileError
)
from src.daemon.exceptions.file_service import FileServiceError
from src.daemon.server import Server
from src.daemon.services.eula_service import EulaService
from src.daemon.services.file_service import FileService
from unittest import mock

SERVER_TEST_SETTINGS = {
    "java": "java",
    "jar_name": "server.jar",
    "key": "123-456-789",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
}


def test_get_eula_status(tmp_path: Path) -> None:
    file_service = FileService()
    eula_service = EulaService(file_service)

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": str(server_folder)})

    with pytest.raises(EulaFileNotFoundError):
        eula_service.get(server)

    eula_file = server_folder / "eula.txt"
    eula_file.touch()

    with pytest.raises(InvalidEulaFileError):
        eula_service.get(server)

    eula_file.write_text("eula=true\n")

    assert eula_service.get(server) is True

    eula_file.write_text("eula=false\n")
    assert eula_service.get(server) is False

    eula_file.write_text("-eula=agagag\n")
    with pytest.raises(InvalidEulaFileError):
        eula_service.get(server)


def test_set_eula_status(tmp_path: Path) -> None:
    file_service = FileService()
    eula_service = EulaService(file_service)

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": str(server_folder)})

    with pytest.raises(EulaFileNotFoundError):
        eula_service.set(server, False)

    eula_file = server_folder / "eula.txt"
    eula_file.touch()

    with pytest.raises(InvalidEulaFileError):
        eula_service.set(server, True)

    eula_file.write_text("eula=false\n")

    assert eula_service.set(server, False)
    assert not eula_service.get(server)

    assert eula_service.set(server, True)
    assert eula_service.get(server)

    with pytest.raises(EulaFileUpdateError):
        with mock.patch.object(FileService, "update_file", side_effect=FileServiceError):
            eula_service.set(server, False)
