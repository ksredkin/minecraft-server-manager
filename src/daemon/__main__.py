import asyncio
from pathlib import Path

from src.common.utils.logger import Logger
from src.daemon.api_client import APIClient
from src.daemon.config_reader import ConfigReader
from src.daemon.exceptions.config import InvalidConfigError
from src.daemon.server import Server
from src.daemon.services.metrics_service import MetricsService

logger = Logger(__name__)


async def main() -> None:
    config = ConfigReader(Path(__file__).resolve().parent / "config.toml").read()

    servers_config = config.get("servers")
    if not isinstance(servers_config, list):
        raise InvalidConfigError("No servers configured.")

    servers: list[Server] = []
    for server_settings in servers_config:
        if not isinstance(server_settings, dict):
            continue
        servers.append(Server(server_settings))

    if not servers:
        raise InvalidConfigError("No servers configured.")

    daemon_settings = config.get("daemon")
    if not isinstance(daemon_settings, dict):
        raise InvalidConfigError(
            "Invalid or missing [daemon] section in configuration."
        )

    api_host = daemon_settings.get("api_host")
    api_port = daemon_settings.get("api_port")
    if not isinstance(api_host, str) or not isinstance(api_port, int):
        raise InvalidConfigError(
            'Invalid "api_host" or "api_port" type in daemon settings.'
        )

    metrics_service = MetricsService()

    api_client = APIClient(api_host, api_port, servers, metrics_service)
    await api_client.connect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user.")
