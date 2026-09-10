from src.common.utils.logger import Logger
from src.daemon.exceptions.eula_service import (
    EulaFileNotFoundError,
    EulaFileReadError,
    EulaFileUpdateError,
    InvalidEulaFileError,
)
from src.daemon.exceptions.file_service import (
    FileServiceError,
    ItemNotFoundError,
)
from src.daemon.server import Server
from src.daemon.services.file_service import FileItem, FileService

logger = Logger(__name__)


class EulaService:
    def __init__(self, file_service: FileService) -> None:
        self.file_service = file_service

    def _get_eula_file(self, server: Server) -> FileItem:
        try:
            eula_file = self.file_service.get_file_item(server, "eula.txt")
        except ItemNotFoundError as e:
            raise EulaFileNotFoundError("EULA file not found.") from e
        except FileServiceError as e:
            raise EulaFileReadError("Failed to read EULA file.") from e

        if eula_file.content is None:
            raise InvalidEulaFileError("EULA file cannot be read as text.")
        if "eula=" not in eula_file.content:
            raise InvalidEulaFileError("EULA status is not set.")

        return eula_file

    def get(self, server: Server) -> bool:
        eula_file = self._get_eula_file(server)
        lines = eula_file.content.splitlines()  # type: ignore

        for line in lines:
            if line.startswith("eula="):
                return line.split("=", 1)[1].rstrip() == "true"

        raise InvalidEulaFileError("EULA status is not set.")

    def set(self, server: Server, accept: bool) -> bool:
        eula_file = self._get_eula_file(server)
        lines = eula_file.content.splitlines()  # type: ignore

        target_value = "true" if accept else "false"
        target_line = f"eula={target_value}"

        new_lines = []
        is_changed = False

        for line in lines:
            if line.startswith("eula="):
                if line == target_line:
                    return True

                new_lines.append(target_line)
                is_changed = True
            else:
                new_lines.append(line)

        if not is_changed:
            return True

        logger.info(f'Updated EULA status: "{"true" if accept else "false"}"')
        try:
            self.file_service.update_file(
                server, "eula.txt", new_content="\n".join(new_lines)
            )
        except FileServiceError as e:
            raise EulaFileUpdateError("Failed to update EULA file.") from e

        return True
