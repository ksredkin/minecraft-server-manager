from unittest.mock import MagicMock, patch

from src.daemon.services.metrics_service import MetricsService


def test_get_metrics_with_no_process():
    metrics_service = MetricsService()
    server = type("Server", (), {"process": None, "ram_limit": 4, "pcu_percent": 0})()

    metrics = metrics_service.get_metrics(server)

    assert metrics["ram_usage"] is None
    assert metrics["ram_limit"] == 4
    assert metrics["cpu_percent"] is None


def test_get_metrics_with_process():
    metrics_service = MetricsService()
    metrics_service.cpu_cores = 4
    process = MagicMock(pid=123)
    process_info = MagicMock(rss=2 * 1024**3)
    server = MagicMock(process=process, ram_limit=4, pcu_percent=37.5)

    with patch("src.daemon.services.metrics_service.psutil.Process") as process_factory:
        process_factory.return_value.memory_info.return_value = process_info

        metrics = metrics_service.get_metrics(server)

    process_factory.assert_called_once_with(123)
    assert metrics == {"ram_usage": 2.0, "ram_limit": 4, "cpu_percent": 9.4}
    