import secrets
from hashlib import sha256

class KeyService:
    def create(self) -> str:
        return secrets.token_urlsafe(32)

    def hash(self, key: str) -> str:
        return sha256(key.encode("utf-8")).hexdigest()

    def verify(self, key: str, hash: str) -> bool:
        return self.hash(key) == hash
