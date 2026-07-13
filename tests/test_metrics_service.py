from types import SimpleNamespace
from unittest.mock import patch

from src.api.services.metrics_service import MetricsService, get_metrics_service


def test_get_memory_usage() -> None:
    memory = SimpleNamespace(total=3 * 1024**3, used=1024**3)

    with patch("src.api.services.metrics_service.virtual_memory", return_value=memory):
        result = MetricsService.get_memory_usage()

    assert result == {"total": 3, "used": 1}


def test_get_metrics_service_returns_singleton() -> None:
    service1 = get_metrics_service()
    service2 = get_metrics_service()

    assert service1 is service2
