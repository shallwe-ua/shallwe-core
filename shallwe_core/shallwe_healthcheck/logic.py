import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.db import connection


logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """
    Health check result:
    - is_healthy
    - message
    - [optional] error
    Serializable (to_dict)
    """

    is_healthy: bool
    message: str
    error: Optional[str] = None

    def to_dict(self) -> dict[str, str]:
        result = {
            "is_healthy": self.is_healthy,
            "message": self.message
        }
        if self.error:
            result["error"] = self.error
        return result


class BaseHealthCheck(ABC):
    """
    Abstract base class for defining health checks.
    To implement:
    - property `name`
    - method `check`
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique check name for reports"""
        pass

    @abstractmethod
    def check(self) -> CheckResult:
        """Perform the specific health check and return result"""
        pass


class DatabaseHealthCheck(BaseHealthCheck):
    """Checks the basic database connection"""

    @property
    def name(self) -> str:
        return "database"

    def check(self) -> CheckResult:
        try:
            connection.ensure_connection()
            return CheckResult(
                is_healthy=True,
                message="Database connection is healthy"
            )
        except Exception as e:  # catches various DB errors
            logger.error(f"{self.name} check failed: {e}")
            return CheckResult(
                is_healthy=False,
                message="Database connection failed",
                error=str(e),
            )


@dataclass
class HealthCheckReport:
    """
    Health check report:
    - version
    - is_healthy
    - checks: {name: {details}}
    Serializable (to_dict)
    """
    version: str
    checks: dict[str, CheckResult]
    is_healthy: bool = True

    def to_dict(self) -> dict:
        return {
            "is_healthy": self.is_healthy,
            "checks": {name: check.to_dict() for name, check in self.checks.items()}
        }


class HealthCheckRunner:
    """
    Runs a list of health checks and aggregates the results.
    Defaults to database health check.
    """

    def __init__(self, checks: list[BaseHealthCheck] | None = None):
        self.checks = checks or [DatabaseHealthCheck()]

    def run_all_checks(self) -> HealthCheckReport:
        checks_results: dict[str, CheckResult] = {}
        overall_healthy = True

        for check in self.checks:
            result = check.check()
            checks_results[check.name] = result
            overall_healthy = overall_healthy and result.is_healthy

        return HealthCheckReport(
            version=settings.SHALLWE_BACKEND_VERSION,
            checks=checks_results,
            is_healthy=overall_healthy
        )
