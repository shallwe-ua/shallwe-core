from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
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

    def _get_response(self, url, method='get', data=None, query_params=None, content_type=MULTIPART_CONTENT, _format=None):
        url_reversed = reverse(url)
        client = self._get_authenticated_client()

        if method == 'get':
            response = client.get(url_reversed, data=query_params)
        else:
            client_http_method = getattr(client, method)

            if 'multipart' in content_type and method not in ('post', 'delete'):
                data = encode_multipart(BOUNDARY, data)

            response = client_http_method(url_reversed, data=data, content_type=content_type, format=_format)

        client.logout()

        return response
