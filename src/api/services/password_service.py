from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordService:
    def __init__(self) -> None:
        self.ph = PasswordHasher()

    def hash(self, password: str) -> str:
        return self.ph.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            self.ph.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False
