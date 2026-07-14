from psutil import virtual_memory


class MetricsService:
    @staticmethod
    def get_ram_usage() -> dict[str, int]:
        ram = virtual_memory()
        return {"total": round(ram.total / 1024**3, 1), "used": round(ram.used / 1024**3, 1)}


service = MetricsService()


def get_metrics_service() -> MetricsService:
    return service
