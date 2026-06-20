from abc import ABC, abstractmethod


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
