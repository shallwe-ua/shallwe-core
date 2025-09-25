from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthCheckIntegrationTest(APITestCase):

    def test_healthcheck_endpoint(self):
        """Should give healthy since db connects before tests"""

        url = reverse("healthcheck")  # Replace with your actual URL name

        # GET request should return JSON with checks
        response = self.client.get(url)

        print('>>>>>> HEALTHCHECK ENDPOINT <<<<<<<')
        print(response.data)

        self.assertIn("checks", response.data)
        self.assertIn("database", response.data["checks"])
        self.assertIn("message", response.data["checks"]["database"])



        # Status code should be 200 if database is healthy
        self.assertEqual(response.status_code, status.HTTP_200_OK)
