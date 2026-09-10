import pytest
from pathlib import Path
from src.daemon.services.file_service import FileService, FolderItem, FileItem
from src.daemon.exceptions.file_service import FileServiceError
from src.daemon.server import Server
from unittest import mock

SERVER_TEST_SETTINGS = {
    "java": "java",
    "jar_name": "server.jar",
    "key": "123-456-789",
    "minecraft_version": "1.21.2",
    "server_software": "spigot",
}


def test_get_relative_path(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    file_path = server_folder / "folder" / "file.txt"
    correct_file_relative_path = Path(server_folder.name) / "folder" / "file.txt"

    assert (
        file_service._get_relative_path(server, file_path) == correct_file_relative_path
    )


def test_get_relative_path_returns_absolute_path_for_path_outside_server(
    tmp_path: Path,
) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})
    outside_path = tmp_path / "outside.txt"

    assert (
        file_service._get_relative_path(server, outside_path) == outside_path.resolve()
    )


def test_get_safe_path(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    assert file_service._get_safe_path(server, None) == server_folder
    assert (
        file_service._get_safe_path(server, Path("folder/file.txt"))
        == server_folder / "folder" / "file.txt"
    )
    with pytest.raises(FileServiceError):
        file_service._get_safe_path(server, "C://")


def test_get_folder_item(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    (server_folder / "not_a_folder").touch()
    folder = server_folder / "folder"
    folder.mkdir()
    (folder / "subfolder").mkdir()
    (folder / "file").touch()

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.get_folder_item(server, "C://")
    with pytest.raises(FileServiceError):
        file_service.get_folder_item(server, "not_existing_folder")
    with pytest.raises(FileServiceError):
        file_service.get_folder_item(server, "not_a_folder")

    assert file_service.get_folder_item(server, "folder") == FolderItem(
        "folder",
        server_folder / "folder",
        [
            FileItem("file", folder / "file", 0),
            FolderItem("subfolder", folder / "subfolder", []),
        ],
    )


def test_get_folder_item_returns_none_when_reading_folder_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "iterdir", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.get_folder_item(server)

def test_write_file(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    file = server_folder / "file" 
    file.write_text("hello, world!", encoding="utf-8")

    not_existing_file = server_folder / "not_existing_file"

    folder = server_folder / "folder"
    folder.mkdir()

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.write_file(server, "C://", "123")
    with pytest.raises(FileServiceError):
        file_service.write_file(server, "file", "123")
    with pytest.raises(FileServiceError):
        file_service.write_file(server, "folder", "123")
    assert file_service.write_file(server, not_existing_file.name, "123") == FileItem(not_existing_file.name, not_existing_file, not_existing_file.stat().st_size, "123")
    assert file_service.write_file(server, "empty_file") == FileItem(
        "empty_file", server_folder / "empty_file", 0, None
    )


def test_write_file_returns_none_when_writing_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "write_text", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.write_file(server, "file", "content")

def test_update_file(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    file = server_folder / "file" 
    file.write_text("hello, world!", encoding="utf-8")

    not_existing_file = server_folder / "not_existing_file"

    folder = server_folder / "folder"
    folder.mkdir()

    new_file_path = server_folder / "new_file"

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.update_file(server, "C://", new_content="123")
    with pytest.raises(FileServiceError):
        file_service.update_file(server, not_existing_file.name, new_content="123")
    with pytest.raises(FileServiceError):
        file_service.update_file(server, folder.name, new_content="123")
    assert file_service.update_file(server, file.name, new_content="new content") == FileItem(file.name, file, file.stat().st_size, "new content")
    assert file_service.update_file(server, file.name, new_path=new_file_path.name) == FileItem(new_file_path.name, new_file_path, new_file_path.stat().st_size, "new content")
    with pytest.raises(FileServiceError):
        file_service.update_file(server, "file", new_path="new_file")


def test_update_file_returns_none_when_reading_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    file = server_folder / "file"
    file.write_text("content", encoding="utf-8")
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "read_text", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.update_file(server, file.name)


def test_update_file_rejects_existing_destination(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    file = server_folder / "file"
    file.write_text("content", encoding="utf-8")
    destination = server_folder / "destination"
    destination.touch()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.update_file(server, file.name, destination.name)

def test_update_folder(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    folder = server_folder / "folder"
    folder.mkdir()

    new_folder_path = server_folder / "new_folder"

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.update_folder(server, "C://", new_path=new_folder_path.name)
    assert file_service.update_folder(server, folder.name, new_path=new_folder_path.name) == FolderItem(new_folder_path.name, new_folder_path, [])


def test_update_folder_rejects_existing_destination(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    folder = server_folder / "folder"
    folder.mkdir()
    destination = server_folder / "destination"
    destination.mkdir()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.update_folder(server, folder.name, destination.name)


def test_update_folder_returns_none_when_renaming_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    folder = server_folder / "folder"
    folder.mkdir()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "rename", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.update_folder(server, folder.name, "new_folder")


def test_update_folder_returns_items_after_renaming(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    folder = server_folder / "folder"
    folder.mkdir()
    (folder / "file").write_text("content", encoding="utf-8")
    (folder / "subfolder").mkdir()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    assert file_service.update_folder(server, folder.name, "renamed") == FolderItem(
        "renamed",
        server_folder / "renamed",
        [
            FileItem("file", server_folder / "renamed" / "file", 7),
            FolderItem("subfolder", server_folder / "renamed" / "subfolder", []),
        ],
    )

def test_get_item(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    folder = server_folder / "folder"
    folder.mkdir()
    (folder / "file").touch()

    file = server_folder / "file" 
    file.write_text("hello, world!", encoding="utf-8")

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.get_item(server, "C://")
    with pytest.raises(FileServiceError):
        file_service.get_item(server, "not_existing")
    assert isinstance(file_service.get_item(server, folder.name), FolderItem)
    assert isinstance(file_service.get_item(server, file.name), FileItem)


def test_get_item_returns_none_for_file_without_item_path(tmp_path: Path) -> None:
    file_service = FileService()
    file = tmp_path / "file"
    file.touch()

    with mock.patch.object(file_service, "_get_safe_path", return_value=file):
        with pytest.raises(FileServiceError):
            file_service.get_item(object(), None)

def test_create_folder(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    folder = server_folder / "folder"
    folder.mkdir()

    new_folder_path = server_folder / "new_folder"

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.create_folder(server, "C://")
    with pytest.raises(FileServiceError):
        file_service.create_folder(server, folder.name)
    assert file_service.create_folder(server, new_folder_path.name) == FolderItem(new_folder_path.name, new_folder_path, [])


def test_create_folder_returns_none_when_creation_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "mkdir", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.create_folder(server, "folder")

def test_delete_item(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    folder = server_folder / "folder"
    folder.mkdir()
    (folder / "file").touch()

    file = server_folder / "file" 
    file.write_text("hello, world!", encoding="utf-8")

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.delete_item(server, "C://")
    with pytest.raises(FileServiceError):
        file_service.delete_item(server, "not_existing")
    file_service.delete_item(server, folder.name)
    file_service.delete_item(server, file.name)


def test_delete_item_returns_false_when_deletion_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    file = server_folder / "file"
    file.touch()
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "unlink", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.delete_item(server, file.name)

def test_get_file_item(tmp_path: Path) -> None:
    file_service = FileService()

    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()

    file = server_folder / "file" 
    file.write_text("hello, world!", encoding="utf-8")

    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with pytest.raises(FileServiceError):
        file_service.get_file_item(server, "C://")
    with pytest.raises(FileServiceError):
        file_service.get_file_item(server, "not_existing")
    assert isinstance(file_service.get_file_item(server, file.name), FileItem)


def test_get_file_item_returns_item_without_content_for_binary_file(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    file = server_folder / "binary"
    file.write_bytes(b"\xff\xfe")
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    assert file_service.get_file_item(server, file.name) == FileItem(
        file.name, file, file.stat().st_size, None
    )


def test_get_file_item_returns_none_when_reading_fails(tmp_path: Path) -> None:
    file_service = FileService()
    server_folder = tmp_path / "server"
    server_folder.mkdir()
    (server_folder / "server.jar").touch()
    file = server_folder / "file"
    file.write_text("content", encoding="utf-8")
    server = Server({**SERVER_TEST_SETTINGS, "path": server_folder})

    with mock.patch.object(Path, "read_text", side_effect=OSError):
        with pytest.raises(FileServiceError):
            file_service.get_file_item(server, file.name)
