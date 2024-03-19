from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from shallwe_profile.models import UserProfile
from shallwe_util.tests import AuthorizedAPITestCase


class ProfileAPIViewTest(AuthorizedAPITestCase):
    fixtures = ['locations_mini_fixture.json']

    def setUp(self):
        self.valid_data_min = {
            'profile[name]': 'Микола',
            'profile[photo]': self._get_image(),
            'rent_preferences[min_budget]': 1000,
            'rent_preferences[max_budget]': 2000,
            'about[birth_date]': '1960-02-02',
            'about[gender]': 1,
            'about[is_couple]': True,
            'about[has_children]': False,
            'rent_preferences[locations]': ['UA01', 'UA05']
        }

    def tearDown(self):
        try:
            self.user.profile.delete()
        except:
            pass

    def _get_response_shortcut(self, data: dict):
        url = 'profile-create'
        method = 'post'
        response = self._get_response(url, method=method, data=data, _format='multipart')
        return response

    def _get_image(self, filename: str = 'valid-format.jpg'):
        from django.contrib.staticfiles import finders
        full_path = finders.find('shallwe_profile/img/' + filename)
        image_file = open(full_path, 'rb')
        return image_file

    def test_valid_profile_creation(self):
        response = self._get_response_shortcut(self.valid_data_min)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(UserProfile.objects.filter(user=self.user)), 1)

    def test_valid_profile_creation_tags_as_strs(self):
        with patch('shallwe_photo.formatcheck.clean_image', lambda x: x), \
             patch('shallwe_photo.facecheck.check_face_minified_temp', lambda x: True):

            data_tags_as_strs = self.valid_data_min | {
                'rent_preferences[locations]': 'UA01',
                'about[other_animals]': 'кіт',
                'about[interests]': 'біг'
            }
            response = self._get_response_shortcut(data_tags_as_strs)
            self.assertEqual(response.status_code, 201)

    def test_valid_profile_creation_min_budget_zero(self):
        with patch('shallwe_photo.formatcheck.clean_image', lambda x: x), \
                patch('shallwe_photo.facecheck.check_face_minified_temp', lambda x: True):

            data_min_budget_zero = self.valid_data_min | {
                'rent_preferences[min_budget]': 0,
            }
            response = self._get_response_shortcut(data_min_budget_zero)
            self.assertEqual(response.status_code, 201)

    def test_invalid_data_response(self):
        with patch('shallwe_photo.formatcheck.clean_image', lambda x: None), \
             patch('shallwe_photo.facecheck.check_face_minified_temp', lambda x: True):

            # Wrong value
            invalid_data_wrong_value = self.valid_data_min | {
                'profile[name]': 'М'
            }
            response1 = self._get_response_shortcut(invalid_data_wrong_value)
            self.assertEqual(response1.status_code, 400)
            self.assertIn('name', response1.data.get('error').get('profile'))

            # Wrong attribute
            invalid_data_wrong_attribute = self.valid_data_min | {
                'profile[hello]': 'Міша',
            }
            response2 = self._get_response_shortcut(invalid_data_wrong_attribute)
            self.assertEqual(response2.status_code, 400)
            self.assertIn('profile[hello]', response2.data.get('error'))


class ProfileVisibilityViewTestCase(AuthorizedAPITestCase):
    def setUp(self):
        self.profile = self.createProfile()

    def createProfile(self):
        from django.contrib.staticfiles import finders
        jpeg_file_path = finders.find('shallwe_profile/img/valid-format.jpg')

        # Open the file, read binary data, and create a SimpleUploadedFile
        with open(jpeg_file_path, 'rb') as jpg_file:
            jpg_file_data = jpg_file.read()
            initial_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")

        # Create a UserProfile instance with an initial JPEG image
        profile = UserProfile.objects.create(
            user=self.user,
            name='ТестЮзер',
            photo_w768=initial_uploaded_file
        )

        return profile

    def tearDown(self):
        try:
            self.user.profile.delete()
        except:
            pass

    def _get_response_shortcut(self, data):
        response = self._get_response('profile-visibility', method='patch', data=data, content_type='application/json')
        return response

    def test_profile_visibility_view_valid(self):
        response = self._get_response_shortcut(data={'is_hidden': True})
        self.assertEqual(response.status_code, 200)

    def test_profile_visibility_view_invalid(self):
        for data, expected_code in (
            ({}, 400),
            ({'hello': 123}, 400),
            ({'is_hidden': None}, 400)
        ):
            response = self._get_response_shortcut(data=data)
            self.assertEqual(response.status_code, expected_code)

    def test_profile_visibility_change_no_profile_conflict(self):
        self.profile.delete()
        response = self._get_response_shortcut(data={'is_hidden': True})
        self.assertEqual(response.status_code, 409)
