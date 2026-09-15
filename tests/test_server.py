from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock
from unittest.mock import Mock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture

from src.daemon.exceptions.server import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
    ServerIsAlreadyRunningError,
    ServerIsNotRunningError,
    ServerJarDoesNotExistError,
    ServerResponseTimeoutError,
)
from src.daemon.server import Server

SERVER_TEST_SETTINGS = {
    "java": "java",
    "jar_name": "server.jar",
    "key": "123-456-789",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
}


def make_server(path: Path) -> Server:
    (path / "server.jar").touch()
    return Server({**SERVER_TEST_SETTINGS, "path": str(path)})


def test_invalid_config_error_raises_if_no_needed_values() -> None:
    with pytest.raises(InvalidServerConfigurationError):
        Server({})


def test_server_folder_does_not_exist_error_raises_if_server_folder_does_not_exist(
    tmp_path: Path,
) -> None:
    with pytest.raises(ServerFolderDoesNotExistError):
        Server({**SERVER_TEST_SETTINGS, "path": str(tmp_path / "not_existing_folder")})


def test_server_jar_does_not_exist_error_raises_if_server_jar_does_not_exist(
    tmp_path: Path,
) -> None:
    with pytest.raises(ServerJarDoesNotExistError):
        Server({**SERVER_TEST_SETTINGS, "path": str(tmp_path)})


def test_parse_memory() -> None:
    assert Server.parse_memory("512KB") == round(512 / 1024**2, 1)
    assert Server.parse_memory("512K") == round(512 / 1024**2, 1)

    assert Server.parse_memory("1.5GB") == round(1.5, 1)
    assert Server.parse_memory("1.5G") == round(1.5, 1)

    assert Server.parse_memory("100MB") == round(100 / 1024, 1)
    assert Server.parse_memory("100M") == round(100 / 1024, 1)

    assert Server.parse_memory("mindustry") is None


def test_start(tmp_path: Path, mocker: MockerFixture) -> None:
    server = make_server(tmp_path)

    mocked_popen = mocker.patch("src.daemon.server.Popen")
    mocked_popen.return_value.poll.return_value = None
    mocked_process = mocker.patch("src.daemon.server.psutil.Process")
    mocked_process.return_value.pid = 123
    mocked_thread = mocker.patch("src.daemon.server.Thread")

    server.start()
    assert server.process is not None, "Server process is not set"

    mocked_popen.assert_called_once()
    mocked_process.assert_called_once()
    mocked_thread.assert_any_call(target=server._reader, daemon=True)
    mocked_thread.assert_any_call(target=server._updater, daemon=True)
    assert mocked_thread.return_value.start.call_count == 2

    with pytest.raises(ServerIsAlreadyRunningError):
        server.start()


def test_reader(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    process_mock = Mock()
    process_mock.stdout.readline.return_value = None

    server.process = process_mock

    server._reader()
    process_mock.wait.assert_called_once_with(timeout=5)
    assert server.process is None

    server.process = process_mock
    server._players_event = Mock()
    server._players_event.set.side_effect = RuntimeError("Players event set called")

    process_mock.stdout.readline.return_value = (
        "There are 2 of a max of 20 players online: player_87, agagagagagag"
    )
    with pytest.raises(RuntimeError):
        server._reader()

    assert set(server._players) == set(["player_87", "agagagagagag"])
    assert server._max_players == 20


def test_execute_command(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    process_mock = Mock()
    process_mock.poll.return_value = None

    server.process = process_mock

    server.execute_command("say Hello World")
    process_mock.stdin.write.assert_called_once_with("say Hello World\n")
    process_mock.stdin.flush.assert_called_once()

    server.process = None

    with pytest.raises(ServerIsNotRunningError):
        server.execute_command("stop")


def test_stop(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    process_mock = Mock()
    process_mock.poll.return_value = None

    server.process = process_mock

    server.stop()
    process_mock.stdin.write.assert_called_once_with("stop\n")
    process_mock.stdin.flush.assert_called_once()

    server.process = None

    with pytest.raises(ServerIsNotRunningError):
        server.stop()


@freeze_time("2026-09-15 8:14:00")
def test_get_uptime(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    server._start_time = None
    assert server.get_uptime() == "0:0:0:0"

    server._start_time = datetime.now() - timedelta(
        days=1, hours=1, minutes=1, seconds=1
    )
    assert server.get_uptime() == "1:1:1:1"


def test_restart(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    process_mock = Mock()
    process_mock.poll.return_value = None

    server.process = process_mock

    with mock.patch.object(
        server, "stop", side_effect=ServerIsNotRunningError("Server is not running.")
    ):
        with pytest.raises(ServerIsNotRunningError):
            server.restart()

    server._stop_event = Mock()
    server._stop_event.wait.return_value = True

    with mock.patch.object(server, "stop") as mock_stop:
        with mock.patch.object(server, "start") as mock_start:
            server.restart()
            server._stop_event.wait.assert_called_once()
            mock_start.assert_called_once()
            mock_stop.assert_called_once()


def test_status(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    server.process = None
    assert server.status() == "stopped"

    server.process = Mock()
    server.process.poll.return_value = None
    assert server.status() == "stopped"

    server._status = "running"
    assert server.status() == "running"

    server._status = "stopped"
    assert server.status() == "stopped"


def test_get_players(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    with pytest.raises(ServerIsNotRunningError):
        server.get_players()

    process_mock = Mock()
    server.process = process_mock
    process_mock.poll.return_value = 1
    with pytest.raises(ServerIsNotRunningError):
        server.get_players()

    process_mock.poll.return_value = None

    server._players_event = Mock()
    server._players_event.return_value = True

    with mock.patch.object(server, "execute_command") as mock_execute_command:
        mock_execute_command.return_value = None
        assert server.get_players() == []

        server._players = ["player1", "player2"]
        assert server.get_players() == ["player1", "player2"]

        server._players = []
        assert server.get_players() == []

    with pytest.raises(ServerResponseTimeoutError):
        server._players_event.wait.return_value = False
        server.get_players()


def test_get_server_info(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    server._status = "running"
    server._players = ["player1", "player2"]
    server._minecraft_version = "1.21.2"
    server._server_software = "spigot"
    server._uptime = "1:0:0:0"
    server._max_players = 20

    expected_info = {
        "status": "running",
        "players": ["player1", "player2"],
        "minecraft_version": "1.21.2",
        "server_software": "spigot",
        "uptime": "1:0:0:0",
        "max_players": 20,
    }

    assert server.get_server_info() == expected_info


def test_get_logs(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    server._logs = deque(["log1", "log2", "log3"])
    assert server.get_logs() == ["log1", "log2", "log3"]


def test_get_pending_logs(tmp_path: Path) -> None:
    server = make_server(tmp_path)

    server._queue.put("log1")
    server._queue.put("log2")
    server._queue.put("log3")

    assert server.get_pending_logs() == ["log1", "log2", "log3"]
