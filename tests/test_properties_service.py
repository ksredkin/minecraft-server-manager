from pathlib import Path
from unittest import mock

import pytest

from src.daemon.exceptions.properties_service import (
    InvalidPropertiesFileError,
    PropertiesFileNotFoundError,
    PropertiesFileReadError,
    PropertiesFileTypeError,
)
from src.daemon.server import Server
from src.daemon.services.file_service import FileItem, FileService
from src.daemon.services.properties_service import PropertiesService

SERVER_TEST_SETTINGS = {
    "java": "java",
    "jar_name": "server.jar",
    "key": "123-456-789",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
}


def test_get_properties(tmp_path: Path) -> None:
    file_service = FileService()
    properties_service = PropertiesService(file_service)

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": str(server_folder)})

    with pytest.raises(PropertiesFileNotFoundError):
        properties_service.get_properties(server)

    properties_file = server_folder / "server.properties"
    properties_file.mkdir()

    with pytest.raises(PropertiesFileTypeError):
        properties_service.get_properties(server)

    properties_file.rmdir()
    properties_file.touch()

    with mock.patch.object(Path, "read_text", side_effect=OSError):
        with pytest.raises(PropertiesFileReadError):
            properties_service.get_properties(server)

    with pytest.raises(InvalidPropertiesFileError):
        properties_service.get_properties(server)

    properties_file.write_text("online_mode=true\n")
    assert properties_service.get_properties(server) == {"online_mode": "true"}


def test_set_property(tmp_path: Path) -> None:
    file_service = FileService()
    properties_service = PropertiesService(file_service)

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": str(server_folder)})

    with pytest.raises(PropertiesFileNotFoundError):
        properties_service.set_property(server, "online_mode", "false")

    properties_file = server_folder / "server.properties"
    properties_file.mkdir()

    with pytest.raises(PropertiesFileTypeError):
        properties_service.set_property(server, "online_mode", "false")

    properties_file.rmdir()
    properties_file.touch()

    with mock.patch.object(Path, "read_text", side_effect=OSError):
        with pytest.raises(PropertiesFileReadError):
            properties_service.set_property(server, "online_mode", "false")

    with pytest.raises(InvalidPropertiesFileError):
        properties_service.set_property(server, "online_mode", "false")

    properties_file.write_text("online_mode=true\n")
    assert properties_service.set_property(server, "online_mode", "false")
    assert properties_service.get_properties(server) == {"online_mode": "false"}


def test_get_properties_file(tmp_path: Path) -> None:
    file_service = FileService()
    properties_service = PropertiesService(file_service)

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": str(server_folder)})

    with pytest.raises(PropertiesFileNotFoundError):
        properties_service._get_properties_file(server)

    properties_file = server_folder / "server.properties"
    properties_file.mkdir()

    with pytest.raises(PropertiesFileTypeError):
        properties_service._get_properties_file(server)

    properties_file.rmdir()
    properties_file.touch()

    with mock.patch.object(Path, "read_text", side_effect=OSError):
        with pytest.raises(PropertiesFileReadError):
            properties_service._get_properties_file(server)

    with pytest.raises(InvalidPropertiesFileError):
        properties_service._get_properties_file(server)

    properties_file.write_text("online_mode=true\n")
    assert properties_service._get_properties_file(server) == FileItem(
        properties_file.name,
        properties_file,
        properties_file.stat().st_size,
        "online_mode=true\n",
    )
