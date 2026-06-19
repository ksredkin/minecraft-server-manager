from abc import ABC, abstractmethod

class ApiClientInterface(ABC):
    @staticmethod
    @abstractmethod
    def search_project(query: str, minecraft_version: str) -> list[str]:
        pass

