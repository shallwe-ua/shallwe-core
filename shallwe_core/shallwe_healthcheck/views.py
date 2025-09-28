from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .logic import HealthCheckRunner


class HealthCheckView(APIView):

    def get(self, request, *args, **kwargs):
        report = self._perform_health_check()
        http_status = status.HTTP_200_OK if report.is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(report.to_dict(), status=http_status)

    def head(self, request, *args, **kwargs):
        report = self._perform_health_check()
        http_status = status.HTTP_200_OK if report.is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(status=http_status)

    def _perform_health_check(self):
        runner = HealthCheckRunner()
        report = runner.run_all_checks()
        return report
