from pathlib import Path
from subprocess import PIPE
from unittest.mock import MagicMock, patch

import pytest

from src.api.exceptions.server import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
    ServerNotRunningError,
)
from src.api.services.process_service import ProcessService, get_process_service


def test_invalid_server_configuration() -> None:
    with pytest.raises(InvalidServerConfigurationError):
        ProcessService(server_path=None)


def test_server_folder_does_not_exist() -> None:
    with pytest.raises(ServerFolderDoesNotExistError):
        ProcessService(server_path="non_existent_folder")


def test_start_and_execute_command(tmp_path: Path) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()

    service = ProcessService(server_path=str(server_dir))
    process = MagicMock()
    process.poll.return_value = None
    process.stdin = MagicMock()
    process.stdout = MagicMock()
    process.stderr = MagicMock()

    with patch("src.api.services.process_service.Popen", return_value=process) as mock_popen, patch(
        "src.api.services.process_service.Thread"
    ), patch("src.api.services.process_service.JAVA", "java"), patch(
        "src.api.services.process_service.JAR_NAME", "server.jar"
    ), patch("src.api.services.process_service.JAVA_ARGS", []), patch(
        "src.api.services.process_service.JAR_ARGS", []
    ):
        assert service.start() is True
        assert service.status() == "running"

        service.execute_command("stop")

    mock_popen.assert_called_once_with(
        ["java", "-jar", "server.jar"],
        cwd=str(server_dir),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    process.stdin.write.assert_called_once_with("stop\n")
    process.stdin.flush.assert_called_once_with()


def test_execute_command_without_running_process(tmp_path: Path) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()

    service = ProcessService(server_path=str(server_dir))

    with pytest.raises(ServerNotRunningError):
        service.execute_command("stop")


def test_get_process_service() -> None:
    service1 = get_process_service()
    service2 = get_process_service()

    assert service1 is service2