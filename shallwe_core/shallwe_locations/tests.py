from rest_framework import status

from shallwe_util.tests import AuthorizedAPITestCase


class LocationSearchViewTestCase(AuthorizedAPITestCase):
    fixtures = ['locations_fixture.json']

    def _get_response_shortcut(self, query: str = None):
        url = 'location-search'
        response = self._get_response(url, method='get', query_params={'query': query})
        return response

    def test_location_search_kyi(self):
        response = self._get_response_shortcut('Киї')
        print(f'>>>>>>>>>>>\n{response.data}\n>>>>>>>>>>>>')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('regions' in response.data)
        self.assertTrue('cities' in response.data)
        self.assertTrue('other_ppls' in response.data)

        self.assertEqual(len(response.data['regions']), 1)
        self.assertEqual(len(response.data['cities']), 1)

        self.assertEqual(response.data['cities'][0]['ppl_name'], 'Київ')
        self.assertEqual(len(response.data['cities'][0]['districts']), 10)

    def test_location_search_ppls_only(self):
        response = self._get_response_shortcut('Бород')
        print(f'>>>>>>>>>>>\n{response.data}\n>>>>>>>>>>>>')

        self.assertTrue(not response.data['regions'])
        self.assertTrue(not response.data['cities'])
        self.assertTrue(response.data['other_ppls'])

    def test_location_search_forbidden_cases(self):
        response1 = self._get_response_shortcut('')
        response2 = self._get_response_shortcut('К')
        response3 = self._get_response_shortcut('К' * 33)

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_location_search_not_found(self):
        response = self._get_response_shortcut('320fdsfsd')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
