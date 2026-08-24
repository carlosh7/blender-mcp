"""
blender-mcp-ultra — Monitoring & Observability
Health checks, metrics, and alerting.
"""

import json
import os
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class HealthStatus:
    """Health check status."""

    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    checks: dict[str, bool]
    details: dict[str, Any]


@dataclass
class Metrics:
    """Performance metrics."""

    request_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    max_response_time: float = 0.0
    active_connections: int = 0
    memory_usage_mb: float = 0.0


class HealthChecker:
    """Health check system."""

    def __init__(self):
        self.checks = {}
        self.last_check = None

    def register_check(self, name: str, check_func: Callable):
        """Register a health check function."""
        self.checks[name] = check_func

    def check_health(self) -> HealthStatus:
        """Run all health checks."""
        results = {}
        details = {}

        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = result.get("healthy", False)
                details[name] = result
            except Exception as e:
                results[name] = False
                details[name] = {"error": str(e)}

        # Determine overall status
        if all(results.values()):
            status = "healthy"
        elif any(results.values()):
            status = "degraded"
        else:
            status = "unhealthy"

        self.last_check = HealthStatus(
            status=status, timestamp=datetime.now().isoformat(), checks=results, details=details
        )

        return self.last_check

    def get_status(self) -> dict[str, Any]:
        """Get current health status."""
        if self.last_check is None:
            self.check_health()
        return asdict(self.last_check)


class MetricsCollector:
    """Metrics collection system."""

    def __init__(self):
        self.metrics = Metrics()
        self._lock = threading.Lock()
        self._response_times = []

    def record_request(self, response_time: float, success: bool):
        """Record a request metric."""
        with self._lock:
            self.metrics.request_count += 1
            if not success:
                self.metrics.error_count += 1

            self._response_times.append(response_time)
            if len(self._response_times) > 1000:
                self._response_times = self._response_times[-1000:]

            self.metrics.avg_response_time = sum(self._response_times) / len(self._response_times)
            self.metrics.max_response_time = max(self._response_times)

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        with self._lock:
            return asdict(self.metrics)

    def reset(self):
        """Reset metrics."""
        with self._lock:
            self.metrics = Metrics()
            self._response_times = []


class AlertManager:
    """Alert management system."""

    def __init__(self, alert_threshold: float = 0.1):
        self.alert_threshold = alert_threshold
        self.alerts = []
        self._lock = threading.Lock()

    def check_alerts(self, metrics: Metrics) -> list[dict[str, Any]]:
        """Check for alert conditions."""
        new_alerts = []

        # High error rate
        if metrics.request_count > 0:
            error_rate = metrics.error_count / metrics.request_count
            if error_rate > self.alert_threshold:
                new_alerts.append(
                    {
                        "type": "high_error_rate",
                        "severity": "warning",
                        "message": f"Error rate: {error_rate:.1%}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # Slow responses
        if metrics.avg_response_time > 5.0:
            new_alerts.append(
                {
                    "type": "slow_responses",
                    "severity": "warning",
                    "message": f"Average response time: {metrics.avg_response_time:.2f}s",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        with self._lock:
            self.alerts.extend(new_alerts)
            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]

        return new_alerts

    def get_alerts(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent alerts."""
        with self._lock:
            return self.alerts[-limit:]


# Singleton instances
_health_checker = None
_metrics_collector = None
_alert_manager = None


def get_health_checker() -> HealthChecker:
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_metrics_collector() -> MetricsCollector:
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_alert_manager() -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def check_health() -> dict[str, Any]:
    """Convenience function to check health."""
    return get_health_checker().get_status()


def get_metrics() -> dict[str, Any]:
    """Convenience function to get metrics."""
    return get_metrics_collector().get_metrics()


def record_metric(response_time: float, success: bool):
    """Convenience function to record metric."""
    get_metrics_collector().record_request(response_time, success)
