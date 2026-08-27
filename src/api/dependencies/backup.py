from src.api.services.backup_manager import BackupManager
from src.common.core.config import secrets, settings


def get_backup_manager() -> BackupManager:
    return BackupManager(
        secrets.get("backup_encryption_key"), settings.backup_storage_path
    )
