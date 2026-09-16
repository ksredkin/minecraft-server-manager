from src.daemon.config_reader import ConfigReader
from src.daemon.exceptions.config import ConfigNotFoundError, InvalidConfigError
from pathlib import Path
import pytest

def test_config_reader(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    with pytest.raises(ConfigNotFoundError):
        ConfigReader(config_path)

    config_path.touch()

    reader = ConfigReader(config_path)
    assert reader.read() == {}

    config_path.write_text("invalid_toml")

    with pytest.raises(InvalidConfigError):
        reader.read()

    toml_data = """[daemon]
api_host = '127.0.0.1'

[[servers]]
path = 'D:/server'
"""
    config_path.write_text(toml_data)
    assert reader.read() == {"daemon": {"api_host": "127.0.0.1"}, "servers": [{"path": "D:/server"}]}
