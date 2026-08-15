import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.auth import auth_router
from src.api.routers.daemon import daemon_router
from src.api.routers.server import server_router
from src.common.core.config import settings

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    app = FastAPI(
        title="Minecraft Server Manager",
        description="API для управления Minecraft серверами.",
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

    app.include_router(auth_router)
    app.include_router(daemon_router)
    app.include_router(server_router)

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)


if __name__ == "__main__":
    main()
