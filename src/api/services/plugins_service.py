from src.common.core.config import SERVER_PATH
from pathlib import Path

class PluginsService:
    def __init__(self, server_path: str = SERVER_PATH) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")
        
        server_dir = Path(server_path)
            
        if not server_dir.exists():
            raise RuntimeError("Папки сервера не существует.")
        
        self.plugins_dir = server_dir / "plugins"

    def get_plugins(self) -> list[str]:
        if not self.plugins_dir.exists():
            raise RuntimeError("Не найдена папка плагинов сервера.")
        
        plugins = []

        for item in self.plugins_dir.iterdir():
            if item.is_file() and item.name.endswith(".jar"):
                plugins.append(item.name[:-4])

        return plugins

plugins_service = PluginsService()

def get_plugins_service() -> PluginsService:
    return plugins_service

