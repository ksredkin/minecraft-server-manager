from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_algorithm: str = "HS256"

    db_user: str
    db_host: str
    db_port: int
    db_name: str

    redis_host: str = "redis"
    redis_port: int = 6379

    api_host: str = "0.0.0.0"
    api_port: int = 8080

    backup_storage_path: str | None = None

    yoocassa_shop_id: str | None = None
    payment_return_url: str | None = None


class Secrets:
    def __init__(self, path: Path = Path("/run/secrets")) -> None:
        self.path = path

    def get(self, name: str) -> str:
        return (self.path / name).read_text().strip()


settings = Settings()  # type: ignore
secrets = Secrets()
