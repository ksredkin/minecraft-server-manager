import tomllib
from pathlib import Path

class ConfigReader:
    def __init__(self, config_path: str) -> None:
        config = Path(config_path)

        if not config.exists():
            raise FileNotFoundError("Не найден файл config.toml.")

        self.config = config

    def read(self) -> dict[str, str|int|dict[str, str|int|list[str]]]:
        with self.config.open("r", encoding="utf-8") as f:
            return tomllib.loads(f.read())
