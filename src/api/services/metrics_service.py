from psutil import virtual_memory


class MetricsService:
    @staticmethod
    def get_memory_usage() -> dict[str, int]:
        memory = virtual_memory()
        return {"total": memory.total // 1024**3, "used": memory.used // 1024**3}


service = MetricsService()


def get_metrics_service() -> MetricsService:
    return service
