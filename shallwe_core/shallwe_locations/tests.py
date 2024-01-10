from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class LocationSearchViewTestCase(TestCase):
    fixtures = ['locations_fixture.json']

    def setUp(self):
        # Create any necessary data or set up the test environment here
        pass

    def _get_response(self, query: str):
        url = reverse('location-search')  # Replace 'location-search' with your URL name
        client = APIClient()
        # Making a GET request to your view with a search term
        response = client.get(url, {'query': query})
        return response

    def test_search_kyi(self):
        response = self._get_response('Киї')
        print(f'>>>>>>>>>>>\n{response.data}\n>>>>>>>>>>>>')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('regions' in response.data)
        self.assertTrue('cities' in response.data)
        self.assertTrue('other_ppls' in response.data)

        self.assertEqual(len(response.data['regions']), 1)
        self.assertEqual(len(response.data['cities']), 1)

        self.assertEqual(response.data['cities'][0]['ppl_name'], 'Київ')
        self.assertEqual(len(response.data['cities'][0]['districts']), 10)

    def test_search_ppls_only(self):
        response = self._get_response('Бород')
        print(f'>>>>>>>>>>>\n{response.data}\n>>>>>>>>>>>>')

        self.assertTrue(not response.data['regions'])
        self.assertTrue(not response.data['cities'])
        self.assertTrue(response.data['other_ppls'])

    def test_forbidden_cases(self):
        response1 = self._get_response('')
        response2 = self._get_response('К')
        response3 = self._get_response('К' * 33)

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_empty(self):
        response = self._get_response('320fdsfsd')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
