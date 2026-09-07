from src.api.services.plugin_service import PluginService
from src.api.api_clients.plugins.modrinth import ModrinthAPIClient
from src.api.api_clients.plugins.interface import PluginsAPIClientInterface
from fastapi import Depends
from src.api.schemas.plugin import plugin_provider
from src.api.exceptions.plugin import UnsupportedPluginProviderError

def get_plugin_service(
    provider: plugin_provider = "modrinth",
) -> PluginService:
    match provider:
        case "modrinth":
            client = ModrinthAPIClient()
        case _:
            raise UnsupportedPluginProviderError(
                f'Unsupported plugin provider: "{provider}".'
            )

    return PluginService(client)
