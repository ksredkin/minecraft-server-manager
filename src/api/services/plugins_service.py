from pathlib import Path
from typing import Any

from src.api.api_clients.interfaces import ApiClientInterface
from src.api.api_clients.modrinth import ModrinthApiClient
from src.common.core.config import MINECRAFT_VERSION, SERVER_PATH, SERVER_SOFTWARE


class PluginsService:
    def __init__(
        self,
        api_client: ApiClientInterface = ModrinthApiClient(),
        server_path: str = SERVER_PATH,
        minecraft_version: str = MINECRAFT_VERSION,
        server_software: str = SERVER_SOFTWARE,
    ) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")

        server_dir = Path(server_path)

        if not server_dir.exists():
            raise RuntimeError("Папки сервера не существует.")

        if not minecraft_version:
            raise ValueError("Не установлена версия minecraft сервера.")

        if not server_software:
            raise ValueError("Не установлен тип ядра сервера.")

        self.plugins_dir = server_dir / "plugins"
        self.api_client = api_client
        self.minecraft_version = minecraft_version
        self.server_software = server_software

    def get_plugins(self) -> list[str]:
        if not self.plugins_dir.exists():
            raise RuntimeError("Не найдена папка плагинов сервера.")

        plugins = []

        for item in self.plugins_dir.iterdir():
            if item.is_file() and item.name.endswith(".jar"):
                plugins.append(item.name[:-4])

        return plugins

    async def search_plugins(
        self, query: str
    ) -> list[dict[str, str | int | list[str] | None]]:
        result = await self.api_client.search_project(query, self.minecraft_version)
        hits = result.get("hits")

        if hits is None:
            raise

        ret: list[Any] = []
        for plugin in hits:
            item: dict[str, Any] = {
                "id": plugin["project_id"],
                "slug": plugin["slug"],
                "title": plugin["title"],
                "description": plugin["description"],
                "downloads": plugin["downloads"],
                "icon_url": plugin["icon_url"],
            }
            ret.append(item)
        return ret

    async def get_plugin_info(
        self, plugin_id_or_slug: str
    ) -> dict[str, str | int | None]:
        return await self.api_client.get_plugin_info(plugin_id_or_slug)

    async def get_plugin_versions(
        self, plugin_id_or_slug: str
    ) -> list[dict[str, str | int | None | list[str]]]:
        return await self.api_client.get_plugin_versions(plugin_id_or_slug)  # type: ignore

    async def install_plugin(self, plugin_id_or_slug: str) -> list[str] | None:
        result = await self.get_plugin_versions(plugin_id_or_slug)

        if result is None:
            return None

        server_software = self.server_software.lower()

        for item in result:
            game_versions_value = item.get("game_versions", [])
            if not isinstance(game_versions_value, list):
                game_versions_value = []

            if self.minecraft_version not in game_versions_value:
                continue

            loaders_value = item.get("loaders", [])
            if not isinstance(loaders_value, list):
                loaders_value = []

            if server_software not in [
                loader.lower() for loader in loaders_value if isinstance(loader, str)
            ]:
                continue

            downloaded: list[str] = []
            files_value = item.get("files")

            if isinstance(files_value, list):
                for file in files_value:
                    if not isinstance(file, dict):
                        continue

                    filename_value = file.get("filename")
                    if not isinstance(filename_value, str):
                        continue

                    download_url = file.get("url")

                    file_path = self.plugins_dir / filename_value
                    await self.api_client.download_plugin(download_url, file_path)
                    downloaded.append(filename_value)

            return downloaded
        return None


plugins_service = PluginsService()


def get_plugins_service() -> PluginsService:
    return plugins_service
