from pathlib import Path
from typing import Any

import pytest

from src.api.exceptions.server import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
)
from src.api.exceptions.settings import SettingsFileNotFoundError
from src.api.services.properties_service import (
    PropertiesService,
    get_properties_service,
)

test_server_properties_string = """#Minecraft server properties
#Mon Jul 06 17:49:49 MSK 2026
max-players=20
online-mode=true"""

test_server_properties_dict = {"max-players": "20", "online-mode": "true"}


def test_properties_service(tmp_path: Any) -> None:
    server_dir_path = Path(str(tmp_path))
    properties_file_path = server_dir_path / "server.properties"

    with properties_file_path.open("w") as f:
        f.write(test_server_properties_string)

    service = PropertiesService(str(server_dir_path))

    assert service.get_properties() == test_server_properties_dict

    service.update_property("online-mode", "false")
    new_properties = test_server_properties_dict.copy()
    new_properties["online-mode"] = "false"
    assert service.get_properties() == new_properties


def test_get_properties_service() -> None:
    service1 = get_properties_service()
    service2 = get_properties_service()

    assert service1 is service2


def test_invalid_server_configuration() -> None:
    with pytest.raises(InvalidServerConfigurationError):
        PropertiesService(server_path=None)  # type: ignore


def test_server_folder_does_not_exist() -> None:
    with pytest.raises(ServerFolderDoesNotExistError):
        PropertiesService(server_path="non_existent_folder")


def test_settings_file_not_found(tmp_path: Any) -> None:
    service = PropertiesService(str(tmp_path))

    with pytest.raises(SettingsFileNotFoundError):
        service.get_properties()

    with pytest.raises(SettingsFileNotFoundError):
        service.update_property("online-mode", "false")
