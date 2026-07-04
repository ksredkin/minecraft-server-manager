import json
from pathlib import Path

from httpx import (
    AsyncClient,
    ConnectError,
    HTTPError,
    NetworkError,
    ProtocolError,
    TimeoutException,
)

from src.api.api_clients.interfaces import ApiClientInterface
from src.common.exceptions import (
    ApiClientConnectionError,
    ApiClientHttpError,
    ApiClientNetworkError,
    ApiClientProtocolError,
    ApiClientTimeoutError,
)


class ModrinthApiClient(ApiClientInterface):
    @staticmethod
    async def search_project(
        query: str, minecraft_version: str
    ) -> dict[str, list[dict[str, str | int | None]]]:
        try:
            async with AsyncClient(timeout=10) as client:
                params = {
                    "query": query,
                    "facets": json.dumps(
                        [[f"versions:{minecraft_version}"], ["project_type:plugin"]]
                    ),
                }
                r = await client.get(
                    "https://api.modrinth.com/v2/search", params=params
                )
                return r.json()  # type: ignore
        except TimeoutException as e:
            raise ApiClientTimeoutError("API не ответил.") from e
        except ConnectError as e:
            raise ApiClientConnectionError("Не удалось подключиться к API.") from e
        except NetworkError as e:
            raise ApiClientNetworkError("Сетевая ошибка при подключении к API.") from e
        except ProtocolError as e:
            raise ApiClientProtocolError(
                "Ошибка протокола при подключении к API."
            ) from e
        except HTTPError as e:
            raise ApiClientHttpError("Ошибка HTTP при подключении к API.") from e

    @staticmethod
    async def get_plugin_info(project_id_or_slug: str) -> dict[str, str | int | None]:
        try:
            async with AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.modrinth.com/v2/project/{project_id_or_slug}"
                )
                return r.json()  # type: ignore
        except TimeoutException as e:
            raise ApiClientTimeoutError("API не ответил.") from e
        except ConnectError as e:
            raise ApiClientConnectionError("Не удалось подключиться к API.") from e
        except NetworkError as e:
            raise ApiClientNetworkError("Сетевая ошибка при подключении к API.") from e
        except ProtocolError as e:
            raise ApiClientProtocolError(
                "Ошибка протокола при подключении к API."
            ) from e
        except HTTPError as e:
            raise ApiClientHttpError("Ошибка HTTP при подключении к API.") from e

    @staticmethod
    async def get_plugin_versions(
        project_id_or_slug: str,
    ) -> list[dict[str, str | int | None]]:
        try:
            async with AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.modrinth.com/v2/project/{project_id_or_slug}/version"
                )
                return r.json()  # type: ignore
        except TimeoutException as e:
            raise ApiClientTimeoutError("API не ответил.") from e
        except ConnectError as e:
            raise ApiClientConnectionError("Не удалось подключиться к API.") from e
        except NetworkError as e:
            raise ApiClientNetworkError("Сетевая ошибка при подключении к API.") from e
        except ProtocolError as e:
            raise ApiClientProtocolError(
                "Ошибка протокола при подключении к API."
            ) from e
        except HTTPError as e:
            raise ApiClientHttpError("Ошибка HTTP при подключении к API.") from e

    @staticmethod
    async def download_plugin(url: str, file_path: Path) -> None:
        try:
            async with AsyncClient(timeout=None) as client:
                r = await client.get(url)

                with file_path.open("wb") as f:
                    f.write(r.content)
        except TimeoutException as e:
            raise ApiClientTimeoutError("API не ответил.") from e
        except ConnectError as e:
            raise ApiClientConnectionError("Не удалось подключиться к API.") from e
        except NetworkError as e:
            raise ApiClientNetworkError("Сетевая ошибка при подключении к API.") from e
        except ProtocolError as e:
            raise ApiClientProtocolError(
                "Ошибка протокола при подключении к API."
            ) from e
        except HTTPError as e:
            raise ApiClientHttpError("Ошибка HTTP при подключении к API.") from e
