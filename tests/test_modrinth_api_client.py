from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import TimeoutException

from src.api.api_clients.modrinth import ModrinthApiClient
from src.api.exceptions.api_client import ApiClientTimeoutError


@pytest.mark.asyncio
async def test_search_project() -> None:
    response = Mock()
    response.json.return_value = {"hits": []}

    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None
    client.get.return_value = response

    with patch("src.api.api_clients.modrinth.AsyncClient", return_value=client):
        result = await ModrinthApiClient.search_project("plugin", "1.21.2")

    assert result == {"hits": []}
    client.get.assert_awaited_once()
    assert client.get.await_args.args[0] == "https://api.modrinth.com/v2/search"
    assert client.get.await_args.kwargs["params"]["query"] == "plugin"


@pytest.mark.asyncio
async def test_download_plugin(tmp_path: Any) -> None:
    file_path = tmp_path / "plugin.jar"
    response = AsyncMock()
    response.content = b"plugin-data"

    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None
    client.get.return_value = response

    with patch("src.api.api_clients.modrinth.AsyncClient", return_value=client):
        await ModrinthApiClient.download_plugin(
            "https://example.com/plugin.jar", file_path
        )

    assert file_path.read_bytes() == b"plugin-data"
    client.get.assert_awaited_once_with("https://example.com/plugin.jar")


@pytest.mark.asyncio
async def test_search_project_timeout_error() -> None:
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = None
    client.get.side_effect = TimeoutException("timeout")

    with patch("src.api.api_clients.modrinth.AsyncClient", return_value=client):
        with pytest.raises(ApiClientTimeoutError):
            await ModrinthApiClient.search_project("plugin", "1.21.2")
