from src.api.api_clients.plugins.modrinth import ModrinthAPIClient
from src.api.exceptions.plugin import UnsupportedPluginProviderError
from src.api.schemas.plugin import plugin_provider
from src.api.services.plugin_service import PluginService


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
