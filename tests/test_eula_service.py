from src.api.services.eula_service import EulaService, get_eula_service
from typing import Any
from pathlib import Path
import pytest
from src.api.exceptions.eula import EulaFileNotFoundError, EulaStatusNotFoundError
from src.api.exceptions.server import InvalidServerConfigurationError, ServerFolderDoesNotExistError


test_eula = """#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).
#Sun Jun 14 16:52:49 MSK 2026
eula=false"""

def test_eula_service(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))
    tmp_eula = tmp_dir / "eula.txt"

    with tmp_eula.open("w") as f:
        f.write(test_eula)

    eula_service = EulaService(server_path=str(tmp_dir))

    assert eula_service.get_eula_status() == False

    eula_service.set_eula_status(True)
    assert eula_service.get_eula_status() == True

    eula_service.set_eula_status(False)
    assert eula_service.get_eula_status() == False


def test_eula_file_not_found(tmp_path: Any) -> None:
    eula_service = EulaService(server_path=str(tmp_path))

    with pytest.raises(EulaFileNotFoundError):
        eula_service.get_eula_status()

    with pytest.raises(EulaFileNotFoundError):
        eula_service.set_eula_status(True)


def test_invalid_server_configuration() -> None:
    with pytest.raises(InvalidServerConfigurationError):
        EulaService(server_path=None)


def test_server_folder_does_not_exist() -> None:
    with pytest.raises(ServerFolderDoesNotExistError):
        EulaService(server_path="non_existent_folder")


def test_eula_status_not_found(tmp_path: Any) -> None:
    tmp_dir = Path(str(tmp_path))
    tmp_eula = tmp_dir / "eula.txt"

    with tmp_eula.open("w") as f:
        f.write("true")

    eula_service = EulaService(server_path=str(tmp_dir))

    with pytest.raises(EulaStatusNotFoundError):
        eula_service.get_eula_status()


def test_get_eula_service() -> None:
    service1 = get_eula_service()
    service2 = get_eula_service()

    assert service1 is service2
