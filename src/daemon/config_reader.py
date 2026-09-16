import tomllib
from tomllib import TOMLDecodeError
from pathlib import Path
from src.daemon.exceptions.config import ConfigNotFoundError, InvalidConfigError


class ConfigReader:
    def __init__(self, config: Path) -> None:
        if not config.exists():
            raise ConfigNotFoundError("config.toml not found.")

        self.config = config

    def read(self) -> dict[str, str | int | dict[str, str | int | list[str]]]:
        try:
            with self.config.open("r", encoding="utf-8") as f:
                return tomllib.loads(f.read())
        except TOMLDecodeError as e:
            raise InvalidConfigError("Invalid config.toml.") from e
