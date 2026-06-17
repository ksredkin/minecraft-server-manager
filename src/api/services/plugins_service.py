from src.common.core.config import SERVER_PATH
import os

class PluginsService:
    def __init__(self, server_path: str = SERVER_PATH) -> None:
        if not server_path:
            raise ValueError("В конфиге не установлен путь к серверу.")

        self.plugins_folder_path = SERVER_PATH.rstrip("/").rstrip("\\") + "/" + "plugins"

    def get_plugins(self) -> list[str]:
        if not os.path.exists(self.plugins_folder_path):
            raise RuntimeError("Не найдена папка плагинов сервера.")

        all_objects = os.listdir(self.plugins_folder_path)
        
        files = []
        for object in all_objects:
            if os.path.isfile(self.plugins_folder_path+"/"+object):
                files.append(object)
        
        plugins = []

        for file in files:
            if file.endswith(".jar"):
                plugins.append(file[0:-4])
        
        return plugins