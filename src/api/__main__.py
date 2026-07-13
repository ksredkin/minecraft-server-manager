import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.core.config import API_HOST, API_PORT
from src.api.exception_handlers import register_exception_handlers
from src.api.routers.backups import backups_router
from src.api.routers.eula import eula_router
from src.api.routers.plugins import plugins_router
from src.api.routers.properties import properties_router
from src.api.routers.server import server_router
from src.api.services.process_service import ProcessService, get_process_service


@asynccontextmanager
async def lifespan(
    app: FastAPI, process_service: ProcessService = get_process_service()
) -> AsyncGenerator[Any, Any]:
    asyncio.create_task(process_service.log_sender())
    yield


def main() -> None:
    app = FastAPI(
        title="Minecraft Server Manager",
        description="API для управления Minecraft сервером.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(server_router)
    app.include_router(backups_router)
    app.include_router(eula_router)
    app.include_router(plugins_router)
    app.include_router(properties_router)

    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    main()
