from src.daemon.api_client import APIClient, Transfer
from pathlib import Path
from src.daemon.exceptions.config import InvalidConfigError
import pytest
from src.daemon.server import Server
from unittest.mock import AsyncMock, Mock, MagicMock
import json
from uuid import uuid4
from unittest import mock
from src.common.enums import DaemonTaskKind

SERVER_TEST_SETTINGS = {
    "java": "java",
    "jar_name": "server.jar",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
}


def test_init_api_client(tmp_path: Path) -> None:
    with pytest.raises(InvalidConfigError):
        APIClient(*[None] * 10)

    with pytest.raises(InvalidConfigError):
        APIClient("127.0.0.1", *[None] * 9)

    with pytest.raises(InvalidConfigError):
        APIClient("127.0.0.1", 8000, *[None] * 8)

    with pytest.raises(InvalidConfigError):
        APIClient("127.0.0.1", 8000, [], *[None] * 7)

    (tmp_path / "server.jar").touch()
    test_server = Server({**SERVER_TEST_SETTINGS, "path": tmp_path, "key": 123})

    with pytest.raises(InvalidConfigError):
        APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)


@pytest.mark.asyncio
async def test_send_json() -> None:
    websocket_mock = AsyncMock()
    test_data = {"hello": "world"}
    await APIClient._send_json(websocket_mock, test_data)
    websocket_mock.send.assert_called_once_with(json.dumps(test_data), text=True)


@pytest.mark.asyncio
async def test_send_bytes() -> None:
    websocket_mock = AsyncMock()
    test_data = "hello world".encode("utf-8")
    await APIClient._send_bytes(websocket_mock, test_data)
    websocket_mock.send.assert_called_once_with(test_data)


def make_server(server_path: Path) -> Server:
    (server_path / "server.jar").touch()
    return Server({**SERVER_TEST_SETTINGS, "path": server_path, "key": "123-456-789"})


@pytest.mark.asyncio
async def test_send_request_response(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()

    data = {"size": 102311231}
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_send_json", new=AsyncMock()
    ) as send_json_mock:
        await api_client._send_request_response(websocket_mock, test_request_id, "request_completed", data=data)
        send_json_mock.assert_called_with(
            websocket_mock, {"id": str(test_request_id), "type": "request_completed", "data": data}
        )
        await api_client._send_request_response(websocket_mock, test_request_id, "request_completed")
        send_json_mock.assert_called_with(
            websocket_mock, {"id": str(test_request_id), "type": "request_completed"}
        )


@pytest.mark.asyncio
async def test_request_completed(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()

    data = {"size": 102311231}
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_send_request_response", new=AsyncMock()
    ) as send_request_response_mock:
        await api_client._request_completed(websocket_mock, test_request_id, data)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_completed", data=data
        )
        await api_client._request_completed(websocket_mock, test_request_id)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_completed"
        )


@pytest.mark.asyncio
async def test_request_failed(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()

    error = "123"
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_send_request_response", new=AsyncMock()
    ) as send_request_response_mock:
        await api_client._request_failed(websocket_mock, test_request_id, error)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_failed", error=error
        )
        await api_client._request_failed(websocket_mock, test_request_id)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_failed"
        )


@pytest.mark.asyncio
async def test_request_accepted(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()

    data = {"hello": "world"}
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_send_request_response", new=AsyncMock()
    ) as send_request_response_mock:
        await api_client._request_accepted(websocket_mock, test_request_id, data)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_accepted", data=data
        )
        await api_client._request_accepted(websocket_mock, test_request_id)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_accepted"
        )


@pytest.mark.asyncio
async def test_request_rejected(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()

    data = {"hello": "world"}
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_send_request_response", new=AsyncMock()
    ) as send_request_response_mock:
        await api_client._request_rejected(websocket_mock, test_request_id, data)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_rejected", data=data
        )
        await api_client._request_rejected(websocket_mock, test_request_id)
        send_request_response_mock.assert_called_with(
            websocket_mock, test_request_id, "request_rejected"
        )


@pytest.mark.asyncio
async def test_handle_request(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_request_completed", new=AsyncMock()
    ) as request_completed_mock:
        async with api_client._handle_request(websocket_mock, test_request_id):
            pass
        request_completed_mock.assert_called_with(
            websocket_mock, test_request_id
        )

    with mock.patch.object(
        api_client, "_request_failed", new=AsyncMock()
    ) as request_failed_mock:
        with mock.patch.object(
            api_client, "_request_completed", new=AsyncMock()
        ) as request_completed_mock:
            request_completed_mock.side_effect = Exception("Internal error.")
            async with api_client._handle_request(websocket_mock, test_request_id):
                pass
        request_failed_mock.assert_called_with(
            websocket_mock, test_request_id, "Internal error."
        )


@pytest.mark.asyncio
async def test_handle_request_without_completed(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient("127.0.0.1", 8000, [test_server], *[None] * 7)

    websocket_mock = AsyncMock()
    test_request_id = uuid4()

    with mock.patch.object(
        api_client, "_request_failed", new=AsyncMock()
    ) as request_failed_mock:
        async with api_client._handle_request(websocket_mock, test_request_id):
            raise Exception("Internal error.")
        request_failed_mock.assert_called_with(
            websocket_mock, test_request_id, "Internal error."
        )


@pytest.mark.asyncio
async def test_create_backup(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    backup_service_mock = AsyncMock()
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 4, backup_service_mock, *[None] * 2
    )

    websocket_mock = AsyncMock()
    test_request_id = uuid4()

    with mock.patch("src.daemon.api_client.asyncio", new=AsyncMock()) as mock_asyncio:
        with mock.patch.object(
            api_client, "_request_completed"
        ) as request_completed_mock:
            backup_mock = Mock()
            backup_mock.name = "123"
            backup_mock.size = 123
            mock_asyncio.to_thread.return_value = backup_mock
            await api_client._create_backup(
                websocket_mock, test_request_id, test_server
            )
            mock_asyncio.to_thread.assert_called_with(
                api_client.backup_service.create, test_server
            )
            request_completed_mock.assert_called_with(
                websocket_mock,
                test_request_id,
                {"name": backup_mock.name, "size": backup_mock.size},
            )

    with mock.patch(
        "src.daemon.api_client.asyncio",
        side_effect=Exception("Backups folder is in server folder."),
    ) as mock_asyncio:
        with mock.patch.object(api_client, "_request_failed") as request_failed_mock:
            backup_mock = Mock()
            backup_mock.name = "123"
            backup_mock.size = 123
            mock_asyncio.to_thread.return_value = backup_mock
            await api_client._create_backup(
                websocket_mock, test_request_id, test_server
            )
            mock_asyncio.to_thread.assert_called_with(
                api_client.backup_service.create, test_server
            )
            request_failed_mock.assert_called_once()


@pytest.mark.asyncio
async def test_restore_backup(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    backup_service_mock = AsyncMock()
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 4, backup_service_mock, *[None] * 2
    )

    websocket_mock = AsyncMock()
    test_request_id = uuid4()

    with mock.patch("src.daemon.api_client.asyncio", new=AsyncMock()) as mock_asyncio:
        with mock.patch.object(
            api_client, "_request_completed"
        ) as request_completed_mock:
            backup_mock = Mock()
            backup_mock.name = "123"
            backup_mock.size = 123
            mock_asyncio.to_thread.return_value = backup_mock
            await api_client._create_backup(
                websocket_mock, test_request_id, test_server
            )
            mock_asyncio.to_thread.assert_called_with(
                api_client.backup_service.create, test_server
            )
            request_completed_mock.assert_called_with(
                websocket_mock,
                test_request_id,
                {"name": backup_mock.name, "size": backup_mock.size},
            )

    with mock.patch(
        "src.daemon.api_client.asyncio",
        side_effect=Exception("Backups folder is in server folder."),
    ) as mock_asyncio:
        with mock.patch.object(api_client, "_request_failed") as request_failed_mock:
            backup_mock = Mock()
            backup_mock.name = "123"
            backup_mock.size = 123
            mock_asyncio.to_thread.return_value = backup_mock
            await api_client._create_backup(
                websocket_mock, test_request_id, test_server
            )
            mock_asyncio.to_thread.assert_called_with(
                api_client.backup_service.create, test_server
            )
            request_failed_mock.assert_called_once()


@pytest.mark.asyncio
async def test_upload_backup(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 7
    )
    
    handle_request_mock = MagicMock()
    
    context_mock = AsyncMock()
    handle_request_mock.return_value = context_mock

    api_client._send_bytes = AsyncMock()

    with mock.patch.object(APIClient, "_handle_request", handle_request_mock):
        
        file_context_mock = AsyncMock()
        file_context_mock.__aenter__.return_value.read = AsyncMock(return_value=b"")
        
        with mock.patch("src.daemon.api_client.aiofiles", MagicMock()) as aiofiles_mock:
            aiofiles_mock.open.return_value = file_context_mock

            websocket_mock = Mock()
            test_request_id = uuid4()
            backup_mock = Mock()
            backup_mock.path = "D://backups/backup123.zip"

            await api_client._upload_backup(websocket_mock, test_request_id, backup_mock)

            handle_request_mock.assert_called_once_with(websocket_mock, test_request_id)


def test_accept_transfer(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 7
    )

    test_request_id = uuid4()
    test_path = tmp_path / "backups" / "backup123.zip"
    test_transfer_kind = DaemonTaskKind.BACKUPS

    api_client._accept_transfer(test_request_id, test_path, test_transfer_kind)

    assert api_client._accepted_transfers[test_request_id] == Transfer(test_path, test_transfer_kind)


def test_accept_backup(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 7
    )

    test_request_id = uuid4()
    test_path = tmp_path / "backups" / "backup123.zip"

    with mock.patch.object(api_client, "_accept_transfer", new=Mock()) as accept_transfer_mock:
        api_client._accept_backup(test_request_id, test_path)
        accept_transfer_mock.assert_called_once_with(test_request_id, test_path, DaemonTaskKind.BACKUPS)

def test_accept_plugin(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 7
    )

    test_request_id = uuid4()
    test_path = tmp_path / "plugins" / "luckperms.jar"

    with mock.patch.object(api_client, "_accept_transfer", new=Mock()) as accept_transfer_mock:
        api_client._accept_plugin(test_request_id, test_path)
        accept_transfer_mock.assert_called_once_with(test_request_id, test_path, DaemonTaskKind.PLUGINS)


@pytest.mark.asyncio
async def test_send_updates(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)

    test_server_info = {
            "status": "stopped",
            "players": [],
            "minecraft_version": "1.21.2",
            "server_software": "spigot",
            "uptime": "0:0:0:0",
            "max_players": None,
    }
    test_server_metrics = {
        "ram_usage": None,
        "ram_limit": 1.2,
        "cpu_percent": None,
    }

    get_server_info_mock = Mock()
    get_server_info_mock.return_value = test_server_info
    test_server.get_server_info = get_server_info_mock

    metrics_service_mock = Mock()
    metrics_service_mock.get_metrics.return_value = test_server_metrics

    get_pending_logs_mock = Mock()
    get_pending_logs_mock.return_value = []
    test_server.get_pending_logs = get_pending_logs_mock

    storage_service_mock = Mock()
    storage_service_mock.get_tasks.return_value = {}
    
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], metrics_service_mock, *[None] * 4, storage_service_mock, None
    )
    
    websocket_mock = AsyncMock()

    with mock.patch("src.daemon.api_client.asyncio", side_effect=Exception()):
        with mock.patch.object(api_client, "_send_json", new=AsyncMock()) as send_json_mock:
            with pytest.raises(Exception):
                await api_client._send_updates(websocket_mock)
            send_json_mock.assert_called_once_with(websocket_mock, {"type": "status", "servers": [{
                                    "key": test_server.key,
                                    "status": test_server_info,
                                    "metrics": test_server_metrics,
                                    "logs": [],
                                    "tasks": {},
                                }]})
            metrics_service_mock.get_metrics.assert_called_once_with(test_server)
            storage_service_mock.get_tasks.assert_called_once_with(str(test_server.key))

"""
@pytest.mark.asyncio
async def test_recieve_commands(tmp_path: Path) -> None:
    test_server = make_server(tmp_path)
    api_client = APIClient(
        "127.0.0.1", 8000, [test_server], *[None] * 7
    )

    websocket_mock = AsyncMock()
    websocket_mock.recv.return_value = b"Hello, World!"

    api_client._recieve_commands()
"""