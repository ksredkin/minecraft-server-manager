from fastapi import FastAPI
import uvicorn
from src.common.core.config import API_HOST, API_PORT
from src.api.routers.backups import backups_router
from src.api.routers.eula import eula_router
from src.api.routers.plugins import plugins_router
from src.api.routers.properties import properties_router
from src.api.routers.server import server_router

def main() -> None:
    app = FastAPI(title="Minecraft Server Manager", description="API для управления Minecraft сервером.")

    app.include_router(server_router)
    app.include_router(backups_router)
    app.include_router(eula_router)
    app.include_router(plugins_router)
    app.include_router(properties_router)

    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    main()
