import asyncio
from pathlib import Path

from src.daemon.api_client import APIClient
from src.daemon.config_reader import ConfigReader
from src.daemon.server import Server


async def main() -> None:
    config = ConfigReader(Path(__file__).resolve().parent / "config.toml").read()

    servers_config = config.get("servers")
    if not isinstance(servers_config, dict):
        raise ValueError("Не добавлен ни 1 сервер.")

    servers: list[Server] = []
    for server_settings in servers_config.values():
        if not isinstance(server_settings, dict):
            continue
        servers.append(Server(server_settings))

    if not servers:
        raise ValueError("Не добавлен ни 1 сервер.")

    daemon_settings = config.get("daemon")
    if not isinstance(daemon_settings, dict):
        raise ValueError("Не найдены настройки daemon.")

    api_host = daemon_settings.get("api_host")
    api_port = daemon_settings.get("api_port")
    if not isinstance(api_host, str) or not isinstance(api_port, int):
        raise ValueError("Не найдены настройки daemon.")

    api_client = APIClient(api_host, api_port, servers)
    await api_client.connect()


if __name__ == "__main__":
    asyncio.run(main())
