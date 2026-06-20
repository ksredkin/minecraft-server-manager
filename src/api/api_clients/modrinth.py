import json

from httpx import AsyncClient

from src.api.api_clients.interfaces import ApiClientInterface


class ModrinthApiClient(ApiClientInterface):
    @staticmethod
    async def search_project(
        query: str, minecraft_version: str
    ) -> dict[str, list[dict[str, str | int | None]]]:
        async with AsyncClient() as client:
            params = {
                "query": query,
                "facets": json.dumps(
                    [[f"versions:{minecraft_version}"], ["project_type:plugin"]]
                ),
            }
            r = await client.get("https://api.modrinth.com/v2/search", params=params)
            return r.json()  # type: ignore

    @staticmethod
    async def get_plugin_info(project_id_or_slug: str) -> dict[str, str | int | None]:
        async with AsyncClient() as client:
            r = await client.get(
                f"https://api.modrinth.com/v2/project/{project_id_or_slug}"
            )
            return r.json()  # type: ignore
