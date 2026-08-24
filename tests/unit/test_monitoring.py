"""
blender-mcp-ultra — Monitoring Tests
Tests for health checks, metrics, and alerting.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestHealthChecker:
    """Tests for Health Checker."""

    def test_health_checker_import(self):
        from src.infrastructure.monitoring import HealthChecker

        assert HealthChecker is not None

    def test_register_check(self):
        from src.infrastructure.monitoring import HealthChecker

        checker = HealthChecker()

        def dummy_check():
            return {"healthy": True}

        checker.register_check("test", dummy_check)
        assert "test" in checker.checks

    def test_check_health(self):
        from src.infrastructure.monitoring import HealthChecker

        checker = HealthChecker()

        def healthy_check():
            return {"healthy": True}

        checker.register_check("test", healthy_check)
        status = checker.check_health()

        assert status.status == "healthy"
        assert status.checks["test"] is True

    def test_check_health_degraded(self):
        from src.infrastructure.monitoring import HealthChecker

        checker = HealthChecker()

        def healthy_check():
            return {"healthy": True}

        def unhealthy_check():
            return {"healthy": False}

        checker.register_check("healthy", healthy_check)
        checker.register_check("unhealthy", unhealthy_check)

        status = checker.check_health()
        assert status.status == "degraded"

    def test_check_health_unhealthy(self):
        from src.infrastructure.monitoring import HealthChecker

        checker = HealthChecker()

        def unhealthy_check():
            return {"healthy": False}

        checker.register_check("test", unhealthy_check)
        status = checker.check_health()

        assert status.status == "unhealthy"

    def test_check_health_error(self):
        from src.infrastructure.monitoring import HealthChecker

        checker = HealthChecker()

        def error_check():
            raise Exception("Test error")

        checker.register_check("test", error_check)
        status = checker.check_health()

        assert status.status == "unhealthy"
        assert "error" in str(status.details["test"])


class TestMetricsCollector:
    """Tests for Metrics Collector."""

    def test_metrics_collector_import(self):
        from src.infrastructure.monitoring import MetricsCollector

        assert MetricsCollector is not None

    def test_record_request(self):
        from src.infrastructure.monitoring import MetricsCollector

        collector = MetricsCollector()

        collector.record_request(0.5, True)
        metrics = collector.get_metrics()

        assert metrics["request_count"] == 1
        assert metrics["error_count"] == 0
        assert metrics["avg_response_time"] == 0.5

    def test_record_error(self):
        from src.infrastructure.monitoring import MetricsCollector

        collector = MetricsCollector()

        collector.record_request(1.0, False)
        metrics = collector.get_metrics()

        assert metrics["request_count"] == 1
        assert metrics["error_count"] == 1

    def test_multiple_requests(self):
        from src.infrastructure.monitoring import MetricsCollector

        collector = MetricsCollector()

        collector.record_request(0.1, True)
        collector.record_request(0.2, True)
        collector.record_request(0.3, True)

        metrics = collector.get_metrics()
        assert metrics["request_count"] == 3
        assert abs(metrics["avg_response_time"] - 0.2) < 0.01

    def test_reset_metrics(self):
        from src.infrastructure.monitoring import MetricsCollector

        collector = MetricsCollector()

        collector.record_request(0.5, True)
        collector.reset()

        metrics = collector.get_metrics()
        assert metrics["request_count"] == 0


class TestAlertManager:
    """Tests for Alert Manager."""

    def test_alert_manager_import(self):
        from src.infrastructure.monitoring import AlertManager

        assert AlertManager is not None

    def test_check_alerts_normal(self):
        from src.infrastructure.monitoring import AlertManager, Metrics

        manager = AlertManager()

        metrics = Metrics(request_count=100, error_count=1)
        alerts = manager.check_alerts(metrics)

        assert len(alerts) == 0

    def test_check_alerts_high_error_rate(self):
        from src.infrastructure.monitoring import AlertManager, Metrics

        manager = AlertManager(alert_threshold=0.1)

        metrics = Metrics(request_count=100, error_count=20)
        alerts = manager.check_alerts(metrics)

        assert len(alerts) > 0
        assert alerts[0]["type"] == "high_error_rate"

    def test_check_alerts_slow_responses(self):
        from src.infrastructure.monitoring import AlertManager, Metrics

        manager = AlertManager()

        metrics = Metrics(request_count=10, avg_response_time=10.0)
        alerts = manager.check_alerts(metrics)

        assert len(alerts) > 0
        assert alerts[0]["type"] == "slow_responses"

    def test_get_alerts(self):
        from src.infrastructure.monitoring import AlertManager, Metrics

        manager = AlertManager()

        # Generate some alerts
        metrics = Metrics(request_count=100, error_count=20)
        manager.check_alerts(metrics)

        alerts = manager.get_alerts(limit=5)
        assert len(alerts) <= 5


class TestSingletons:
    """Tests for singleton instances."""

    def test_health_checker_singleton(self):
        from src.infrastructure.monitoring import get_health_checker

        checker1 = get_health_checker()
        checker2 = get_health_checker()
        assert checker1 is checker2

    def test_metrics_collector_singleton(self):
        from src.infrastructure.monitoring import get_metrics_collector

        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        assert collector1 is collector2

    def test_alert_manager_singleton(self):
        from src.infrastructure.monitoring import get_alert_manager

        manager1 = get_alert_manager()
        manager2 = get_alert_manager()
        assert manager1 is manager2


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_check_health(self):
        from src.infrastructure.monitoring import check_health

        status = check_health()
        assert "status" in status
        assert "checks" in status

    def test_get_metrics(self):
        from src.infrastructure.monitoring import get_metrics

        metrics = get_metrics()
        assert "request_count" in metrics

    def test_record_metric(self):
        from src.infrastructure.monitoring import get_metrics, record_metric

        record_metric(0.5, True)
        metrics = get_metrics()
        assert metrics["request_count"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
