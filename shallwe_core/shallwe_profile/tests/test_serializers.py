from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase

from shallwe_locations.models import Location
from ..models import UserProfile
from ..serializers import UserProfileRentPreferencesSerializer


class UserProfileRentPreferencesSerializerTestCase(TestCase):
    fixtures = ['locations_mini_fixture.json']

    def setUp(self):
        self.profile = self.createProfile()

    def createProfile(self):
        from django.contrib.staticfiles import finders
        user = User.objects.create_user(username='testuser', password='testpassword')
        jpeg_file_path = finders.find('shallwe_profile/img/valid-format.jpg')

        # Open the file, read binary data, and create a SimpleUploadedFile
        with open(jpeg_file_path, 'rb') as jpg_file:
            jpg_file_data = jpg_file.read()
            initial_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")

        # Create a UserProfile instance with an initial JPEG image
        profile = UserProfile.objects.create(
            user=user,
            name='ТестЮзер',
            photo_w768=initial_uploaded_file
        )

        return profile

    def tearDown(self):
        self.profile.delete()

    def test_rent_preferences_default_values_creation(self):
        data = {
            'min_budget': 1000,
            'max_budget': 2000,
        }

        # Validate
        serializer = UserProfileRentPreferencesSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Create the instance
        rent_preferences = serializer.save(user_profile=self.profile)
        self.assertIsNotNone(rent_preferences)

        # Assert the values
        self.assertEqual(rent_preferences.min_budget, 1000)
        self.assertEqual(rent_preferences.max_budget, 2000)
        self.assertEqual(rent_preferences.min_rent_duration_level, 1)
        self.assertEqual(rent_preferences.max_rent_duration_level, 5)
        self.assertEqual(rent_preferences.room_sharing_level, 2)

        # Check locations set
        saved_location = list(rent_preferences.locations.all())
        default_location = [Location.get_all_country()]
        self.assertListEqual(saved_location, default_location)

    def test_rent_preferences_valid_values_creation(self):
        data = {
            'min_budget': 1000,
            'max_budget': 2000,
            'min_rent_duration_level': 1,
            'max_rent_duration_level': 2,
            'room_sharing_level': 1,
            'locations': ['UA01', 'UA05']
        }

        # Validate
        serializer = UserProfileRentPreferencesSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Create the instance
        rent_preferences = serializer.save(user_profile=self.profile)
        self.assertIsNotNone(rent_preferences)

        # Assert the values
        self.assertEqual(rent_preferences.min_budget, 1000)
        self.assertEqual(rent_preferences.max_budget, 2000)
        self.assertEqual(rent_preferences.min_rent_duration_level, 1)
        self.assertEqual(rent_preferences.max_rent_duration_level, 2)
        self.assertEqual(rent_preferences.room_sharing_level, 1)

        # Check locations set
        saved_locations = list(rent_preferences.locations.all())
        passed_locations = list(Location.objects.filter(hierarchy__in=data['locations']))
        self.assertListEqual(saved_locations, passed_locations)

    def _assert_data_invalid(self, data: dict):
        serializer = UserProfileRentPreferencesSerializer(data=data)
        self.assertFalse(serializer.is_valid())    # Expect validation to fail

    def _assert_data_set_all_invalid(self, data_set: list[dict]):
        for data in data_set:
            self._assert_data_invalid(data)

    def test_rent_preferences_invalid_values(self):
        data_budget_min_gt_max = {
            'min_budget': 1000,
            'max_budget': 500,
        }
        data_budget_too_big = {
            'min_budget': 999999,
            'max_budget': 9999999,
        }
        data_budget_minus = {
            'min_budget': -100,
            'max_budget': 100,
        }
        data_rent_duration_not_both_provided = {
            'min_budget': 1000,
            'max_budget': 1500,
            'min_rent_duration_level': 1
        }
        data_rent_duration_min_gt_max = {
            'min_budget': 1000,
            'max_budget': 1500,
            'min_rent_duration_level': 5,
            'max_rent_duration_level': 3
        }
        data_locations_overlap = {
            'min_budget': 1000,
            'max_budget': 2000,
            'locations': ['UA', 'UA01']
        }
        data_locations_nonexistent = {
            'min_budget': 1000,
            'max_budget': 2000,
            'locations': ['UA02']
        }
        self._assert_data_set_all_invalid([
            data_budget_min_gt_max,
            data_budget_too_big,
            data_budget_minus,
            data_rent_duration_not_both_provided,
            data_rent_duration_min_gt_max,
            data_locations_overlap,
            data_locations_nonexistent
        ])
