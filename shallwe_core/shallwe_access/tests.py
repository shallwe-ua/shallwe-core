from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status

from shallwe_util.tests import AuthorizedAPITestCase


class GetProfileStatusViewTest(AuthorizedAPITestCase):
    def test_user_not_logged_in(self):
        response = self._get_response('profile-status', authenticated=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_logged_in_no_profile(self):
        response = self._get_response('profile-status')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_logged_in_with_profile(self):
        # Patch the user.profile property to return the mock UserProfile instance
        with patch.object(User, 'profile') as mock_get_profile:
            mock_get_profile.return_value = True

            response = self._get_response('profile-status')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
