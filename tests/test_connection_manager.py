from src.api.services.connection_manager import ConnectionManager, get_connection_manager
from unittest.mock import AsyncMock
from pytest import mark


@mark.asyncio
async def test_connection_manager() -> None:
    manager = ConnectionManager()

    mock_socket = AsyncMock()
    mock_socket.accept.returns_value = None
    mock_socket.send_text.returns_value = lambda x: x

    await manager.connect(mock_socket)
    await manager.broadcast("123")

    mock_socket.accept.assert_called_once()
    mock_socket.send_text.assert_called_once_with("123")


def test_get_connection_manager() -> None:
    manager1 = get_connection_manager()
    manager2 = get_connection_manager()

    assert manager1 is manager2
