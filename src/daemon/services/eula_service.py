from src.common.utils.logger import Logger
from src.daemon.server import Server
from src.daemon.services.file_service import FileService

logger = Logger(__name__)


class EulaService:
    def __init__(self, file_service: FileService) -> None:
        self.file_service = file_service

    def get(self, server: Server) -> bool | None:
        eula_file = self.file_service.get_file_item(server, "eula.txt")
        if not eula_file or eula_file.content is None:
            return None

        lines = eula_file.content.splitlines()

        for line in lines:
            if line.startswith("eula="):
                return line.split("=")[1].rstrip() == "true"

        return None

    def set(self, server: Server, accept: bool) -> bool:
        eula_file = self.file_service.get_file_item(server, "eula.txt")
        if not eula_file or eula_file.content is None:
            return False

        lines = eula_file.content.splitlines()

        is_changed = False
        for i, line in enumerate(lines):
            if line.startswith("eula="):
                if accept:
                    lines[i] = "eula=true"
                else:
                    lines[i] = "eula=false"
                is_changed = True

        if is_changed:
            logger.info(f'Updated EULA status: "{"true" if accept else "false"}"')
            self.file_service.update_file(
                server, "eula.txt", new_content="\n".join(lines)
            )

        return is_changed
