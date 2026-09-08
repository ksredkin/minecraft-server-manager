import json
from typing import Any, AsyncGenerator

from httpx import (
    AsyncClient,
    ConnectError,
    HTTPError,
    NetworkError,
    ProtocolError,
    TimeoutException,
)

from src.api.api_clients.plugins.interface import PluginsAPIClientInterface
from src.api.exceptions.api_client import (
    APIClientConnectionError,
    APIClientHttpError,
    APIClientNetworkError,
    APIClientProtocolError,
    APIClientTimeoutError,
)


class ModrinthAPIClient(PluginsAPIClientInterface):
    @staticmethod
    async def search_project(
        query: str, minecraft_version: str, server_software: str
    ) -> dict[str, list[dict[str, str | int | None]]]:
        try:
            async with AsyncClient(timeout=10) as client:
                params = {
                    "query": query,
                    "facets": json.dumps(
                        [
                            [f"versions:{minecraft_version}"],
                            ["project_type:plugin"],
                            [f"categories:{server_software}"],
                        ]
                    ),
                }
                r = await client.get(
                    "https://api.modrinth.com/v2/search", params=params
                )
                return r.json()  # type: ignore
        except TimeoutException as e:
            raise APIClientTimeoutError("The API did not respond.") from e
        except ConnectError as e:
            raise APIClientConnectionError("Failed to connect to the API.") from e
        except NetworkError as e:
            raise APIClientNetworkError(
                "Network error while connecting to the API."
            ) from e
        except ProtocolError as e:
            raise APIClientProtocolError(
                "Protocol error while connecting to the API."
            ) from e
        except HTTPError as e:
            raise APIClientHttpError("HTTP error while connecting to the API.") from e

    @staticmethod
    async def get_plugin_info(project_id_or_slug: str) -> dict[str, str | int | None]:
        try:
            async with AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.modrinth.com/v2/project/{project_id_or_slug}"
                )
                r.raise_for_status()
                return r.json()  # type: ignore
        except TimeoutException as e:
            raise APIClientTimeoutError("The API did not respond.") from e
        except ConnectError as e:
            raise APIClientConnectionError("Failed to connect to the API.") from e
        except NetworkError as e:
            raise APIClientNetworkError(
                "Network error while connecting to the API."
            ) from e
        except ProtocolError as e:
            raise APIClientProtocolError(
                "Protocol error while connecting to the API."
            ) from e
        except HTTPError as e:
            raise APIClientHttpError("HTTP error while connecting to the API.") from e

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
            raise APIClientTimeoutError("The API did not respond.") from e
        except ConnectError as e:
            raise APIClientConnectionError("Failed to connect to the API.") from e
        except NetworkError as e:
            raise APIClientNetworkError(
                "Network error while connecting to the API."
            ) from e
        except ProtocolError as e:
            raise APIClientProtocolError(
                "Protocol error while connecting to the API."
            ) from e
        except HTTPError as e:
            raise APIClientHttpError("HTTP error while connecting to the API.") from e

    @staticmethod
    async def download_plugin(url: str, chunk_size: int) -> AsyncGenerator[bytes, Any]:
        try:
            async with AsyncClient(timeout=None) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()

                    async for chunk in response.aiter_bytes(chunk_size):
                        yield chunk
        except TimeoutException as e:
            raise APIClientTimeoutError("The API did not respond.") from e
        except ConnectError as e:
            raise APIClientConnectionError("Failed to connect to the API.") from e
        except NetworkError as e:
            raise APIClientNetworkError(
                "Network error while connecting to the API."
            ) from e
        except ProtocolError as e:
            raise APIClientProtocolError(
                "Protocol error while connecting to the API."
            ) from e
        except HTTPError as e:
            raise APIClientHttpError("HTTP error while connecting to the API.") from e
