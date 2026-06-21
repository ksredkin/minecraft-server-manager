from abc import ABC, abstractmethod
from pathlib import Path


class ApiClientInterface(ABC):
    @staticmethod
    @abstractmethod
    async def search_project(
        query: str, minecraft_version: str
    ) -> dict[str, list[dict[str, str | int | None]]]:
        pass

    @staticmethod
    @abstractmethod
    async def get_plugin_info(project_id_or_slug: str) -> dict[str, str | int | None]:
        pass

    @staticmethod
    @abstractmethod
    async def get_plugin_versions(
        project_id_or_slug: str,
    ) -> list[dict[str, str | int | None]]:
        pass

    @staticmethod
    @abstractmethod
    async def download_plugin(url: str, file_path: Path) -> None:
        pass
