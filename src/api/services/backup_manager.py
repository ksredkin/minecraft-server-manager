import asyncio
import secrets
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.api.dependencies.auth import get_password_service
from src.api.dependencies.billing import get_yookassa_provider
from src.api.exceptions.api import ConfigurationError
from src.api.services.backup_cipher import BackupCipher, get_backup_cipher
from src.api.services.payment_service import PaymentService
from src.api.services.subscription_service import SubscriptionService
from src.api.services.task_manager import TaskManager, get_task_manager
from src.api.services.user_service import UserService
from src.common.core.config import secrets as app_secrets
from src.common.core.config import settings
from src.common.database.connection import session
from src.common.repositories.payment_repository import PaymentRepository
from src.common.repositories.subscription_repository import SubscriptionRepository
from src.common.repositories.user_repository import UserRespository
from src.common.services.cache_service import CacheService, get_cache_service


@dataclass
class Backup:
    name: str
    path: Path
    size: int


class BackupManager:
    def __init__(
        self,
        encryption_key: str,
        storage_path: str,
        task_manager: TaskManager,
        sessionmaker: async_sessionmaker[AsyncSession],
        cache_service: CacheService,
        backup_cipher: BackupCipher,
    ):
        self.encryption_key = encryption_key
        self.storage_path = Path(storage_path)
        self.task_manager = task_manager
        self.sessionmaker = sessionmaker
        self.cache_service = cache_service
        self.backup_cipher = backup_cipher
        self._upload_reservations: dict[int | UUID, dict[UUID, int]] = {}
        self._accepted_tasks: dict[UUID, str] = {}

        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)

    def get_folder_storage_usage(self, folder: Path) -> int:
        usage = 0
        for item in folder.rglob("*"):
            if item.is_file():
                usage += item.stat().st_size
        return usage

    def start_encrypt_backup(self, task_id: UUID, backup: Path) -> bytes:
        nonce = secrets.token_bytes(12)
        self.backup_cipher.create_encryptor(task_id, nonce)

        with backup.open("wb") as f:
            f.write(nonce)

        return nonce

    def complete_backup_encryption(self, task_id: UUID, backup: Path) -> bytes | None:
        tag = self.backup_cipher.finalize_encryptor(task_id)
        if tag is None:
            return None

        with backup.open("ab") as f:
            f.write(tag)

        return tag

    async def reserve(
        self, server_id: int, task_id: UUID, size: int, backup_name: str
    ) -> bool:
        async with self.sessionmaker() as session:
            subscription_service = SubscriptionService(
                SubscriptionRepository(session),
                PaymentService(PaymentRepository(session), get_yookassa_provider()),
            )
            user_service = UserService(
                UserRespository(session), get_password_service(), subscription_service
            )

            owner = await user_service.get_server_owner(server_id)
            if not owner:
                return False

            cloud_limit = await subscription_service.get_user_cloud_backups_limit(
                owner.id
            )
            if cloud_limit == 0:
                return False

            cloud_limit_bytes = cloud_limit * 1024 * 1024 * 1024

            reserved = sum(
                [
                    size
                    for size in self._upload_reservations.get(server_id, {}).values()
                ],
            )
            if reserved == cloud_limit_bytes:
                return False

            server_backups_folder = self.storage_path / f"server_{str(server_id)}"
            if not server_backups_folder.exists():
                server_backups_folder.mkdir(parents=True, exist_ok=True)

            used = await asyncio.to_thread(
                self.get_folder_storage_usage, server_backups_folder
            )
            if (cloud_limit_bytes - used - reserved) < (size + 12 + 16):
                return False

            backup = (server_backups_folder / backup_name).with_suffix(".enc")
            if backup.exists():
                return False

            if server_id not in self._upload_reservations:
                self._upload_reservations[server_id] = {}

            self._upload_reservations[server_id][task_id] = size
            self._accepted_tasks[task_id] = backup_name

            self.start_encrypt_backup(task_id, backup)
            return True

    def get_server_backups(self, server_id: UUID) -> list[Backup]:
        server_backups_folder = self.storage_path / f"server_{str(server_id)}"

        if not server_backups_folder.exists():
            return []

        return [
            Backup(item.name, item, item.stat().st_size)
            for item in server_backups_folder.iterdir()
        ]

    async def handle_chunk(self, bytes: bytes) -> None:
        if len(bytes) < 24:
            return

        task_id_bytes = bytes[:16]
        try:
            task_id = UUID(bytes=task_id_bytes)
        except ValueError:
            return

        backup_name = self._accepted_tasks.get(task_id, None)
        if not backup_name:
            return

        server_id = self.task_manager.get_server_id_by_task(task_id)
        if not server_id:
            return

        chunk = bytes[16:]

        server_backups_folder = self.storage_path / f"server_{str(server_id)}"
        if not server_backups_folder.exists():
            server_backups_folder.mkdir(parents=True, exist_ok=True)

        backup = (server_backups_folder / backup_name).with_suffix(".enc")

        encrypted_chunk = self.backup_cipher.encode(task_id, chunk)
        if encrypted_chunk is not None:
            with backup.open("ab") as f:
                f.write(encrypted_chunk)
        else:
            return

        self.task_manager.add_progress(
            server_id,
            task_id,
            len(chunk),
        )

        if self.task_manager.get_task_completion_percent(server_id, task_id) == 100:
            self._accepted_tasks.pop(task_id)

            if server_id in self._upload_reservations:
                if task_id in self._upload_reservations[server_id]:
                    self._upload_reservations[server_id].pop(task_id, None)

            self.complete_backup_encryption(task_id, backup)


if not settings.backup_storage_path or not isinstance(
    settings.backup_storage_path, str
):
    raise ConfigurationError("BACKUP_STORAGE_PATH must be a string!")

backup_manager = BackupManager(
    app_secrets.get("backup_encryption_key"),
    settings.backup_storage_path,
    get_task_manager(),
    session,
    get_cache_service(),
    get_backup_cipher(),
)


def get_backup_manager() -> BackupManager:
    return backup_manager
