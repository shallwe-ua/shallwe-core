from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AuthorizedAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def _get_authenticated_client(self):
        client = Client()
        client.login(username='testuser', password='testpassword')
        csrftoken_cookie = client.cookies.get('csrftoken', '')
        client.defaults['HTTP_X_CSRFTOKEN'] = csrftoken_cookie
        return client

    def _get_response(self, url, method='get', data=None, query_params=None, _format=None):
        url_reversed = reverse(url)
        client = self._get_authenticated_client()

        if method == 'get':
            response = client.get(url_reversed, data=query_params)
        elif method == 'post':
            response = client.post(url_reversed, data=data, format=_format)
        else:
            response = None

        client.logout()

        return response
