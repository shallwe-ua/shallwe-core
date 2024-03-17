from unittest.mock import patch

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase

from shallwe_locations.models import Location
from ..models import UserProfile, UserProfileRentPreferences, UserProfileAbout
from ..serializers import UserProfileRentPreferencesSerializer
from ..serializers.about import UserProfileAboutSerializer
from ..serializers.profile import UserProfileWithParametersSerializer, NotValidatedDataSavingError


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

    def test_rent_preferences_valid_values_creation_min_budget_zero(self):
        data = {
            'min_budget': 0,
            'max_budget': 2000,
            'min_rent_duration_level': 1,
            'max_rent_duration_level': 2,
            'room_sharing_level': 1,
            'locations': ['UA01', 'UA05']
        }

        # Validate
        serializer = UserProfileRentPreferencesSerializer(data=data)
        self.assertTrue(serializer.is_valid())

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
        data_too_many_locations = {
            'min_budget': 1000,
            'max_budget': 2000,
            'locations': [f'UA{i:02d}' for i in range(1, 32)]
        }
        self._assert_data_set_all_invalid([
            data_budget_min_gt_max,
            data_budget_too_big,
            data_budget_minus,
            data_rent_duration_not_both_provided,
            data_rent_duration_min_gt_max,
            data_locations_overlap,
            data_locations_nonexistent,
            data_too_many_locations
        ])


class UserProfileAboutSerializerTestCase(TestCase):
    def setUp(self):
        self.profile = self.createProfile()
        self.valid_data = {
            'birth_date': '1960-02-02',
            'gender': 1,
            'is_couple': True,
            'has_children': False,
            'other_animals': ['кіт', 'собачка'],  # Valid other animals tags
            'interests': ['спорт', 'музика'],  # Valid interests tags
        }

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

    def test_valid_data_creation_with_defaults(self):
        # Define valid data for the UserProfileAbout instance
        valid_data = self.valid_data

        # Serialize the valid data
        serializer = UserProfileAboutSerializer(data=valid_data)

        # Check if the data is valid
        self.assertTrue(serializer.is_valid())

        # Save the serializer data to create a UserProfileAbout instance
        instance = serializer.save(user_profile=self.profile)

        # Check that the other_animals_tags and interests_tags are set correctly
        self.assertEqual(instance.other_animals_tags.all().count(), 2)
        self.assertEqual(instance.interests_tags.all().count(), 2)

    def test_invalid_data_custom_validations(self):
        def _test_with_invalids(invalid_data_part: dict, error_keys: list = None):
            valid_data = self.valid_data

            corrupted_data = valid_data | invalid_data_part

            serializer = UserProfileAboutSerializer(data=corrupted_data)
            self.assertFalse(serializer.is_valid())

            keys_list = error_keys if error_keys else invalid_data_part.keys()
            for key in keys_list:
                self.assertIn(key, serializer.errors)

            return serializer

        invalid_data_too_young = {
            'birth_date': '2015-02-02'
        }
        _test_with_invalids(invalid_data_too_young)

        invalid_data_too_old = {
            'birth_date': '1900-02-02'
        }
        _test_with_invalids(invalid_data_too_old)

        invalid_data_smoking_type_set_while_not_smoking = {
            'smoking_level': 1,
            'smokes_iqos': True
        }
        _test_with_invalids(invalid_data_smoking_type_set_while_not_smoking, error_keys=['non_field_errors'])

        invalid_data_smoking_type_not_set_while_smoking = {
            'smoking_level': 2
        }
        _test_with_invalids(invalid_data_smoking_type_not_set_while_smoking, error_keys=['non_field_errors'])

        invalid_data_repeated_tags = {
            'other_animals': ['кіт', 'кіт'],
            'interests': ['кіно', 'кіно']
        }
        _test_with_invalids(invalid_data_repeated_tags)

        invalid_data_more_than_5_tags = {
            'other_animals': ['миша', 'собака', 'черепаха', 'пташка', 'бульбашка', 'слоник'],
            'interests': ['дружба', 'жвачка', 'кіно', 'співати', 'гарний день', 'прогулянки по парку']
        }
        _test_with_invalids(invalid_data_more_than_5_tags)

        invalid_data_wrong_regex_tags = {
            'other_animals': ['к іт'],
            'interests': ['г']
        }
        _test_with_invalids(invalid_data_wrong_regex_tags)


class UserProfileSerializerTestCase(TestCase):
    fixtures = ['locations_mini_fixture.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.valid_photo = self.getPhoto()
        self.valid_name = 'Іван'
        self.valid_rent_preferences = {
            'min_budget': 1000,
            'max_budget': 2000
        }
        self.valid_about = {
            'birth_date': '1960-02-02',
            'gender': 1,
            'is_couple': True,
            'has_children': False,
        }

        # Lambda functions for mocked methods. Usage "with patch("original.method.path", new=self.mock_method)"
        self.mock_clean_image = lambda x: Image.open(self.valid_photo)
        self.mock_check_face = lambda x: True

    def getPhoto(self, filename: str = 'valid-format.jpg') -> SimpleUploadedFile:
        from django.contrib.staticfiles import finders
        jpeg_file_path = finders.find(f'shallwe_profile/img/{filename}')

        # Open the file, read binary data, and create a SimpleUploadedFile
        with open(jpeg_file_path, 'rb') as jpg_file:
            jpg_file_data = jpg_file.read()
            initial_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")

        return initial_uploaded_file

    def test_valid_profile_creation_deletion(self):
        serializer_data = {
            'profile': {
                'name': self.valid_name,
                'photo': self.valid_photo,
            },
            'rent_preferences': self.valid_rent_preferences,
            'about': self.valid_about
        }

        serializer = UserProfileWithParametersSerializer(data=serializer_data)

        validity_result = serializer.is_valid()
        self.assertTrue(validity_result.is_all_valid)

        profile = serializer.save(kwargs={'profile': {'user': self.user}})
        self.assertEqual(profile.rent_preferences.locations.count(), 1)

        # Also test related models are deleted when profile is deleted
        profile.delete()
        self.assertEqual(UserProfileRentPreferences.objects.count(), 0)

    def test_invalid_data(self):
        # Invalid name
        invalid_name_data = {
            'profile': {
                'name': 'R00000',
                'photo': self.valid_photo,
            },
            'rent_preferences': self.valid_rent_preferences,
            'about': self.valid_about
        }

        with patch('shallwe_photo.formatcheck.clean_image', self.mock_clean_image), \
             patch('shallwe_photo.facecheck.check_face_minified_temp', self.mock_check_face):
            invalid_name_serializer = UserProfileWithParametersSerializer(data=invalid_name_data)
            self.assertFalse(invalid_name_serializer.is_valid(), 'Invalid name should not pass validation')

        # Invalid photo
        for invalid_photo_filename in ('non-square.jpg', 'cat-face.jpg'):
            invalid_photo_data = {
                'profile': {
                    'name': self.valid_name,
                    'photo': self.getPhoto(invalid_photo_filename),
                },
                'rent_preferences': self.valid_rent_preferences,
                'about': self.valid_about
            }

            invalid_photo_serializer = UserProfileWithParametersSerializer(data=invalid_photo_data)
            self.assertFalse(invalid_photo_serializer.is_valid(),
                             f'Invalid photo "{invalid_photo_filename}" should not pass validation')

        # Invalid rent preferences
        invalid_rent_prefs_data = {
            'profile': {
                'name': self.valid_name,
                'photo': self.valid_photo,
            },
            'rent_preferences': {
                'min_budget': 1000
            },
            'about': self.valid_about
        }

        with patch('shallwe_photo.formatcheck.clean_image', self.mock_clean_image), \
             patch('shallwe_photo.facecheck.check_face_minified_temp', self.mock_check_face):
            invalid_rent_prefs_serializer = UserProfileWithParametersSerializer(data=invalid_rent_prefs_data)
            self.assertFalse(invalid_rent_prefs_serializer.is_valid(),
                             'Invalid rent preferences should not pass validation')

        # Test it's not saving with invalid data
        with self.assertRaises(NotValidatedDataSavingError):
            invalid_rent_prefs_serializer.save()

        # Invalid about
        invalid_about_data = {
            'profile': {
                'name': self.valid_name,
                'photo': self.valid_photo
            },
            'rent_preferences': self.valid_rent_preferences,
            'about': self.valid_about | {'birth_date': '1900-02-02'}
        }
        with patch('shallwe_photo.formatcheck.clean_image', self.mock_clean_image), \
             patch('shallwe_photo.facecheck.check_face_minified_temp', self.mock_check_face):
            invalid_about_serializer = UserProfileWithParametersSerializer(data=invalid_about_data)
            self.assertFalse(invalid_about_serializer.is_valid(),
                             'Invalid about should not pass validation')

        # Test it's not saving with invalid data
        with self.assertRaises(NotValidatedDataSavingError):
            invalid_rent_prefs_serializer.save()

    def tearDown(self):
        UserProfile.objects.filter(user=self.user).delete()
