from pathlib import Path

from src.api.api_clients.interfaces import ApiClientInterface
from src.api.api_clients.modrinth import ModrinthApiClient
from src.common.core.config import MINECRAFT_VERSION, SERVER_PATH


class PluginsService:
    def __init__(
        self,
        api_client: ApiClientInterface = ModrinthApiClient(),
        server_path: str = SERVER_PATH,
    ) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")

        server_dir = Path(server_path)

        if not server_dir.exists():
            raise RuntimeError("Папки сервера не существует.")

        self.plugins_dir = server_dir / "plugins"
        self.api_client = api_client

    def get_plugins(self) -> list[str]:
        if not self.plugins_dir.exists():
            raise RuntimeError("Не найдена папка плагинов сервера.")

        plugins = []

        for item in self.plugins_dir.iterdir():
            if item.is_file() and item.name.endswith(".jar"):
                plugins.append(item.name[:-4])

        return plugins

    async def search_plugins(self, query: str) -> list[dict[str, str | int | None]]:
        result = await self.api_client.search_project(query, MINECRAFT_VERSION)
        hits = result.get("hits")

        if hits is None:
            raise

        return [
            {
                "id": plugin["project_id"],
                "slug": plugin["slug"],
                "title": plugin["title"],
                "description": plugin["description"],
                "downloads": plugin["downloads"],
                "icon_url": plugin["icon_url"],
            }
            for plugin in hits
        ]

    async def get_plugin_info(
        self, plugin_id_or_slug: str
    ) -> dict[str, str | int | None]:
        return await self.api_client.get_plugin_info(plugin_id_or_slug)


plugins_service = PluginsService()


def get_plugins_service() -> PluginsService:
    return plugins_service
