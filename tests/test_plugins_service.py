from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.api.exceptions.api_client import ApiClientInvalidResponseError
from src.api.exceptions.plugins import (
    PluginJarNotFoundError,
    PluginsFolderDoesNotExistError,
    PluginVersionNotFoundError,
)
from src.api.exceptions.server import (
    InvalidServerConfigurationError,
    ServerFolderDoesNotExistError,
)
from src.api.services.plugins_service import PluginsService, get_plugins_service


def test_invalid_server_configuration(tmp_path: Any) -> None:
    with pytest.raises(InvalidServerConfigurationError):
        PluginsService(server_path=None)  # type: ignore

    with pytest.raises(InvalidServerConfigurationError):
        PluginsService(server_path=str(tmp_path), minecraft_version="")

    with pytest.raises(InvalidServerConfigurationError):
        PluginsService(server_path=str(tmp_path), server_software="")


def test_server_folder_does_not_exist() -> None:
    with pytest.raises(ServerFolderDoesNotExistError):
        PluginsService(server_path="non_existent_folder")


def test_get_plugins(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()
    plugins_dir = server_dir / "plugins"
    plugins_dir.mkdir()

    (plugins_dir / "plugin-one.jar").write_text("")
    (plugins_dir / "plugin-two.jar").write_text("")
    (plugins_dir / "readme.txt").write_text("")

    service = PluginsService(
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    assert service.get_plugins() == ["plugin-one", "plugin-two"]


def test_get_plugins_folder_does_not_exist(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()

    service = PluginsService(
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    with pytest.raises(PluginsFolderDoesNotExistError):
        service.get_plugins()


def test_delete_plugin(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()
    plugins_dir = server_dir / "plugins"
    plugins_dir.mkdir()

    plugin_path = plugins_dir / "plugin.jar"
    plugin_path.write_text("")

    service = PluginsService(
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    assert service.delete_plugin("plugin") == "plugin"
    assert not plugin_path.exists()

    with pytest.raises(PluginJarNotFoundError):
        service.delete_plugin("plugin")


@pytest.mark.asyncio
async def test_search_plugins(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()

    api_client = AsyncMock()
    api_client.search_project.return_value = {
        "hits": [
            {
                "project_id": "1",
                "slug": "plugin-slug",
                "title": "Plugin",
                "description": "desc",
                "downloads": 10,
                "icon_url": "https://example.com/icon.png",
            }
        ]
    }

    service = PluginsService(
        api_client=api_client,
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    result = await service.search_plugins("plugin")

    assert result == [
        {
            "id": "1",
            "slug": "plugin-slug",
            "title": "Plugin",
            "description": "desc",
            "downloads": 10,
            "icon_url": "https://example.com/icon.png",
        }
    ]
    api_client.search_project.assert_awaited_once_with("plugin", "1.21.2")


@pytest.mark.asyncio
async def test_search_plugins_invalid_response(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()

    api_client = AsyncMock()
    api_client.search_project.return_value = {}

    service = PluginsService(
        api_client=api_client,
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    with pytest.raises(ApiClientInvalidResponseError):
        await service.search_plugins("plugin")


@pytest.mark.asyncio
async def test_install_plugin(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()
    plugins_dir = server_dir / "plugins"
    plugins_dir.mkdir()

    api_client = AsyncMock()
    api_client.get_plugin_versions.return_value = [
        {
            "game_versions": ["1.21.2"],
            "loaders": ["Spigot"],
            "files": [
                {"filename": "plugin.jar", "url": "https://example.com/plugin.jar"}
            ],
        }
    ]

    service = PluginsService(
        api_client=api_client,
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    result = await service.install_plugin("plugin")

    assert result == ["plugin.jar"]
    api_client.download_plugin.assert_awaited_once_with(
        "https://example.com/plugin.jar",
        plugins_dir / "plugin.jar",
    )


@pytest.mark.asyncio
async def test_install_plugin_not_found(tmp_path: Any) -> None:
    server_dir = tmp_path / "server"
    server_dir.mkdir()

    api_client = AsyncMock()
    api_client.get_plugin_versions.return_value = [
        {
            "game_versions": ["1.20.1"],
            "loaders": ["Paper"],
            "files": [
                {"filename": "plugin.jar", "url": "https://example.com/plugin.jar"}
            ],
        }
    ]

    service = PluginsService(
        api_client=api_client,
        server_path=str(server_dir),
        minecraft_version="1.21.2",
        server_software="spigot",
    )

    with pytest.raises(PluginVersionNotFoundError):
        await service.install_plugin("plugin")


def test_get_plugins_service() -> None:
    service1 = get_plugins_service()
    service2 = get_plugins_service()

    assert service1 is service2
