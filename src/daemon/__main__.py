from src.daemon.config_reader import ConfigReader
from pathlib import Path
from src.daemon.server import Server
from src.daemon.api_client import APIClient
import asyncio

async def main():
    config = ConfigReader(Path(__file__).resolve().parent / "config.toml").read()

    if not "servers" in config:
        raise ValueError("Не добавлен ни 1 сервер.")

    servers = []

    for server_settings in config["servers"]:
        servers.append(Server(server_settings))

    daemon_settings = config.get("daemon")

    if not daemon_settings:
        raise ValueError("Не найдены настройки daemon.")

    api_client = APIClient(daemon_settings.get("api_host"), daemon_settings.get("api_port"), servers)
    await api_client.connect()


if __name__ == "__main__":
    asyncio.run(main())
