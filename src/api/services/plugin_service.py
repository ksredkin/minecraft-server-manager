from typing import Any, AsyncGenerator

from src.api.api_clients.plugins.interface import PluginsAPIClientInterface


class PluginService:
    def __init__(self, api_client: PluginsAPIClientInterface):
        self.api_client = api_client

    async def search(
        self, query: str, minecraft_version: str, server_software: str
    ) -> dict[str, list[dict[str, str | int | None]]]:
        return await self.api_client.search_project(
            query, minecraft_version, server_software
        )

    async def get_plugin_info(
        self, project_id_or_slug: str
    ) -> dict[str, str | int | None]:
        return await self.api_client.get_plugin_info(project_id_or_slug)

    async def get_plugin_versions(
        self,
        project_id_or_slug: str,
    ) -> list[dict[str, str | int | None]]:
        return await self.api_client.get_plugin_versions(project_id_or_slug)

    async def download_plugin(self, url: str) -> AsyncGenerator[bytes, Any]:
        async for chunk in self.api_client.download_plugin(url, 1024 * 1024):
            yield chunk
