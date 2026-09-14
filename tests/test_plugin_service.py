from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.daemon.exceptions.file_service import FileServiceError
from src.daemon.exceptions.plugin import (
    PluginNotFoundError,
    PluginsFolderDoesNotExistError,
)
from src.daemon.server import Server
from src.daemon.services.file_service import FileItem, FolderItem
from src.daemon.services.plugin_service import Plugin, PluginService

SERVER_TEST_SETTINGS = {
    "java": "java",
    "jar_name": "server.jar",
    "key": "123-456-789",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
}


def make_server(path: Path) -> Server:
    path.mkdir()
    (path / "server.jar").touch()
    return Server({**SERVER_TEST_SETTINGS, "path": str(path)})


def make_service() -> tuple[PluginService, MagicMock, MagicMock]:
    file_service = MagicMock()
    storage_service = MagicMock()
    return PluginService(file_service, storage_service), file_service, storage_service


def test_get_plugins_free_storage(tmp_path: Path) -> None:
    service, file_service, storage_service = make_service()
    server = make_server(tmp_path / "server")
    plugins_path = server.server_dir / "plugins"
    file_service.get_folder_item.return_value = FolderItem(
        "plugins", plugins_path, []
    )
    storage_service.get_disk_free_space.return_value = 123

    assert service.get_plugins_free_storage(server) == 123

    file_service.get_folder_item.assert_called_once_with(server, "plugins")
    storage_service.get_disk_free_space.assert_called_once_with(plugins_path)


def test_get_plugins_free_storage_raises_when_plugins_folder_is_missing(
    tmp_path: Path,
) -> None:
    service, file_service, _ = make_service()
    server = make_server(tmp_path / "server")
    file_service.get_folder_item.side_effect = FileServiceError

    with pytest.raises(PluginsFolderDoesNotExistError):
        service.get_plugins_free_storage(server)


def test_get_plugin_returns_plugin_and_none_when_file_is_missing(
    tmp_path: Path,
) -> None:
    service, file_service, _ = make_service()
    server = make_server(tmp_path / "server")
    plugin_path = server.server_dir / "plugins" / "luckperms.jar"
    file_service.get_file_item.return_value = FileItem(
        "luckperms.jar", plugin_path, 42
    )

    assert service.get_plugin(server, "luckperms.jar") == Plugin(
        "Luckperms", plugin_path, 42
    )
    file_service.get_file_item.assert_called_once_with(
        server, str(Path("plugins") / "luckperms.jar")
    )

    file_service.get_file_item.side_effect = FileServiceError
    assert service.get_plugin(server, "missing.jar") is None


def test_get_plugins_returns_only_jar_files(tmp_path: Path) -> None:
    service, file_service, _ = make_service()
    server = make_server(tmp_path / "server")
    plugins_path = server.server_dir / "plugins"
    file_service.get_folder_item.return_value = FolderItem(
        "plugins",
        plugins_path,
        [
            FileItem("luckperms.jar", plugins_path / "luckperms.jar", 42),
            FileItem("notes.txt", plugins_path / "notes.txt", 10),
            FolderItem("config", plugins_path / "config", []),
        ],
    )

    assert service.get_plugins(server) == [
        Plugin("Luckperms", plugins_path / "luckperms.jar", 42)
    ]


def test_delete_plugin_and_map_file_service_errors(tmp_path: Path) -> None:
    service, file_service, _ = make_service()
    server = make_server(tmp_path / "server")

    service.delete(server, "luckperms.jar")
    file_service.delete_item.assert_called_once_with(
        server, str(server.server_dir / "plugins" / "luckperms.jar")
    )

    with pytest.raises(PluginNotFoundError):
        service.delete(server, "luckperms.txt")

    file_service.delete_item.side_effect = FileServiceError
    with pytest.raises(PluginNotFoundError):
        service.delete(server, "vault.jar")


def test_handle_chunk_appends_bytes(tmp_path: Path) -> None:
    service, _, _ = make_service()
    plugin_path = tmp_path / "plugin.jar"

    service.handle_chunk(plugin_path, b"first")
    service.handle_chunk(plugin_path, b" second")

    assert plugin_path.read_bytes() == b"first second"