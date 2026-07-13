from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routers.backups import backups_router
from src.api.routers.eula import eula_router
from src.api.routers.plugins import plugins_router
from src.api.routers.properties import properties_router
from src.api.routers.server import server_router
from src.api.services.backup_service import get_backup_service
from src.api.services.eula_service import get_eula_service
from src.api.services.plugins_service import get_plugins_service
from src.api.services.process_service import get_process_service
from src.api.services.properties_service import get_properties_service


def build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(server_router)
    app.include_router(backups_router)
    app.include_router(eula_router)
    app.include_router(plugins_router)
    app.include_router(properties_router)
    return app


def test_server_routes() -> None:
    app = build_app()
    process_service = MagicMock()
    process_service.start.return_value = True
    process_service.restart.return_value = True
    process_service.status.return_value = "running"
    process_service.get_logs.return_value = ["one", "two", "three"]
    process_service.get_players.return_value = ["Steve"]
    process_service.get_server_info.return_value = {"version": "1.21.2"}

    app.dependency_overrides[get_process_service] = lambda: process_service

    with TestClient(app) as client:
        start_response = client.post("/start")
        stop_response = client.post("/stop")
        restart_response = client.post("/restart")
        status_response = client.get("/status")
        command_response = client.post("/command", params={"command": "stop"})
        logs_response = client.get("/logs")
        logs_tail_response = client.get("/logs/tail", params={"limit": 2})
        players_response = client.get("/players")
        info_response = client.get("/info")

    assert start_response.status_code == 200
    assert start_response.json() == {"success": True}
    assert stop_response.status_code == 200
    assert stop_response.json() == {"success": True}
    assert restart_response.status_code == 200
    assert restart_response.json() == {"success": True}
    assert status_response.status_code == 200
    assert status_response.json() == {"success": True, "data": {"status": "running"}}
    assert command_response.status_code == 200
    assert command_response.json() == {"success": True}
    assert logs_response.status_code == 200
    assert logs_response.json() == {
        "success": True,
        "data": {"logs": ["one", "two", "three"]},
    }
    assert logs_tail_response.status_code == 200
    assert logs_tail_response.json() == {
        "success": True,
        "data": {"logs": ["three", "two"]},
    }
    assert players_response.status_code == 200
    assert players_response.json() == {"success": True, "data": {"players": ["Steve"]}}
    assert info_response.status_code == 200
    assert info_response.json() == {
        "success": True,
        "data": {"info": {"version": "1.21.2"}},
    }


def test_backup_routes() -> None:
    app = build_app()
    backup_service = MagicMock()
    backup_service.get_backups.return_value = ["backup1.zip"]
    backup_service.create_backup.return_value = "backup2.zip"

    app.dependency_overrides[get_backup_service] = lambda: backup_service

    with TestClient(app) as client:
        get_response = client.get("/backups/")
        create_response = client.post("/backups/")
        restore_response = client.post("/backups/restore/backup1.zip")
        delete_response = client.delete("/backups/backup1.zip")

    assert get_response.status_code == 200
    assert get_response.json() == {
        "success": True,
        "data": {"backups": ["backup1.zip"]},
    }
    assert create_response.status_code == 201
    assert create_response.json() == {
        "success": True,
        "data": {"backup": "backup2.zip"},
    }
    assert restore_response.status_code == 200
    assert restore_response.json() == {
        "success": True,
        "data": {"backup": "backup1.zip"},
    }
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "success": True,
        "data": {"backup": "backup1.zip"},
    }


def test_eula_routes() -> None:
    app = build_app()
    eula_service = MagicMock()
    eula_service.get_eula_status.return_value = True

    app.dependency_overrides[get_eula_service] = lambda: eula_service

    with TestClient(app) as client:
        get_response = client.get("/eula/")
        set_response = client.post("/eula/", params={"accept_eula": False})

    assert get_response.status_code == 200
    assert get_response.json() == {"success": True, "data": {"eula": True}}
    assert set_response.status_code == 200
    assert set_response.json() == {"success": True, "data": {"eula": False}}


def test_plugins_routes() -> None:
    app = build_app()
    plugins_service = MagicMock()
    plugins_service.get_plugins.return_value = ["plugin-a", "plugin-b"]
    plugins_service.search_plugins = AsyncMock(return_value=[{"id": "1"}])
    plugins_service.get_plugin_info = AsyncMock(return_value={"name": "plugin-a"})
    plugins_service.install_plugin = AsyncMock(return_value=["plugin-a.jar"])
    plugins_service.delete_plugin.return_value = "plugin-a"

    app.dependency_overrides[get_plugins_service] = lambda: plugins_service

    with TestClient(app) as client:
        list_response = client.get("/plugins/")
        search_response = client.get("/plugins/search", params={"query": "plugin"})
        info_response = client.get(
            "/plugins/info", params={"project_id_or_slug": "plugin-a"}
        )
        install_response = client.post("/plugins/install/plugin-a")
        delete_response = client.delete("/plugins/delete/plugin-a")

    assert list_response.status_code == 200
    assert list_response.json() == {
        "success": True,
        "data": {"plugins": ["plugin-a", "plugin-b"]},
    }
    assert search_response.status_code == 200
    assert search_response.json() == {
        "success": True,
        "data": {"plugins": [{"id": "1"}]},
    }
    assert info_response.status_code == 200
    assert info_response.json() == {
        "success": True,
        "data": {"plugin-a": {"name": "plugin-a"}},
    }
    assert install_response.status_code == 201
    assert install_response.json() == {
        "success": True,
        "data": {"plugin-a": ["plugin-a.jar"]},
    }
    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True, "data": {"plugin": "plugin-a"}}


def test_properties_routes() -> None:
    app = build_app()
    properties_service = MagicMock()
    properties_service.get_properties.return_value = {"difficulty": "easy"}

    app.dependency_overrides[get_properties_service] = lambda: properties_service

    with TestClient(app) as client:
        get_response = client.get("/properties/")
        update_response = client.put("/properties/difficulty", params={"value": "hard"})

    assert get_response.status_code == 200
    assert get_response.json() == {
        "success": True,
        "data": {"properties": {"difficulty": "easy"}},
    }
    assert update_response.status_code == 200
    assert update_response.json() == {"success": True, "data": {"difficulty": "hard"}}
