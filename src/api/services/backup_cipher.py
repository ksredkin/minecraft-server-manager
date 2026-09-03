from uuid import UUID

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.base import (
    AEADDecryptionContext,
    AEADEncryptionContext,
)

from src.api.exceptions.api import ConfigurationError
from src.common.core.config import secrets as api_secrets


class BackupCipher:
    def __init__(self) -> None:
        backup_encryption_key = api_secrets.get("backup_encryption_key")

        if not isinstance(backup_encryption_key, str):
            raise ConfigurationError("backup_encryption_key is not set.")

        if not len(backup_encryption_key) == 32:
            raise ConfigurationError("backup_encryption_key must be 256 bits long.")

        self.key = backup_encryption_key.encode()

        self.encryptors: dict[UUID, AEADEncryptionContext] = {}
        self.decryptors: dict[UUID, AEADDecryptionContext] = {}

    def create_encryptor(self, encryptor_id: UUID, nonce: bytes) -> None:
        self.encryptors[encryptor_id] = Cipher(
            algorithms.AES(self.key), modes.GCM(nonce)
        ).encryptor()

    def create_decryptor(self, decryptor_id: UUID, nonce: bytes) -> None:
        self.decryptors[decryptor_id] = Cipher(
            algorithms.AES(self.key), modes.GCM(nonce)
        ).decryptor()

    def encode(self, encryptor_id: UUID, data: bytes) -> bytes | None:
        encryptor = self.encryptors.get(encryptor_id)
        if not encryptor:
            return None

        return encryptor.update(data)

    def decode(self, decryptor_id: UUID, data: bytes) -> bytes | None:
        decryptor = self.decryptors.get(decryptor_id)
        if not decryptor:
            return None

        return decryptor.update(data)

    def finalize_encryptor(self, encryptor_id: UUID) -> bytes | None:
        encryptor = self.encryptors.pop(encryptor_id, None)
        if encryptor is None:
            return None

        encryptor.finalize()
        return encryptor.tag

    def finalize_decryptor(self, decryptor_id: UUID, tag: bytes) -> None:
        decryptor = self.decryptors.pop(decryptor_id, None)
        if decryptor is None:
            return None

        decryptor.finalize_with_tag(tag)


backup_cipher = BackupCipher()


def get_backup_cipher() -> BackupCipher:
    return backup_cipher
