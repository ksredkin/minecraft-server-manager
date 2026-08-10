from datetime import datetime, timedelta, timezone

import jwt


class JwtService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.algorithm = algorithm
        self.secret_key = secret_key

    def encode(self, user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        }
        return jwt.encode(payload, self.secret_key, self.algorithm)

    def decode(self, token: str) -> int:
        payload = jwt.decode(token, self.secret_key, [self.algorithm])
        return int(payload["sub"])
