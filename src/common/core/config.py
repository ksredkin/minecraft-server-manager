from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    redis_host: str = "redis"
    redis_port: int = 6379

    api_host: str = "0.0.0.0"
    api_port: int = 8080


settings = Settings()  # type: ignore
