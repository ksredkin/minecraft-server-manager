import psutil

from src.daemon.server import Server


class MetricsService:
    def __init__(self) -> None:
        self.cpu_cores: int = psutil.cpu_count(logical=True) or 1

    def get_metrics(self, server: Server) -> dict[str, int | float | None]:
        if server.process is None:
            return {
                "ram_usage": None,
                "ram_limit": server.ram_limit,
                "cpu_percent": None,
            }

        process = psutil.Process(server.process.pid)

        return {
            "ram_usage": round((process.memory_info().rss / 1024 / 1024 / 1024), 1),
            "ram_limit": server.ram_limit,
            "cpu_percent": round(server.pcu_percent / self.cpu_cores, 1),
        }
