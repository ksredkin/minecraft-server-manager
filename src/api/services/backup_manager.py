from pathlib import Path
from uuid import UUID
from dataclasses import dataclass


@dataclass
class Backup:
    name: str
    path: Path
    size: int


class BackupManager:
    def __init__(self, encryption_key: str, storage_path: str):
        self.encryption_key = encryption_key
        self.storage_path = Path(storage_path)

        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)

    def get_server_backups(self, server_id: UUID) -> list[Backup]:
        server_backups_folder = self.storage_path / f"server_{str(server_id)}"

        if not server_backups_folder.exists():
            return []

        return [
            Backup(item.name, item, item.stat().st_size)
            for item in server_backups_folder.iterdir()
        ]
