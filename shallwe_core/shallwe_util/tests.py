from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class AuthorizedAPITestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        cls.token = Token.objects.create(user=cls.user)

    def _get_authenticated_client(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        return client

    def _get_response(self, url, method='get', data=None, query_params=None):
        url_reversed = reverse(url)
        client = self._get_authenticated_client()

        if method == 'get':
            response = client.get(url_reversed, data=query_params)
        else:
            response = client.post(url_reversed, data=data)

        client.credentials()  # Reset credentials

        return response
