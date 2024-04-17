import datetime

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ...models import UserProfile, UserProfileRentPreferences, UserProfileAbout
from ...serializers import UserProfileWithParametersCreateUpdateSerializer, UserProfileVisibilityUpdateSerializer


class UserProfileWithParametersSerializerUpdateTestCase(TestCase):
    fixtures = ['locations_mini_fixture.json']

    def setUp(self):
        self.profile = self.createProfile()

        # Lambda functions for mocked methods. Usage "with patch("original.method.path", new=self.mock_method)"
        self.mock_clean_image = lambda x: Image.open(x)
        self.mock_check_face = lambda x: True

    def getPhoto(self, filename: str = 'valid-format.jpg') -> SimpleUploadedFile:
        from django.contrib.staticfiles import finders
        jpeg_file_path = finders.find(f'shallwe_profile/img/{filename}')

        # Open the file, read binary data, and create a SimpleUploadedFile
        with open(jpeg_file_path, 'rb') as jpg_file:
            jpg_file_data = jpg_file.read()
            initial_uploaded_file = SimpleUploadedFile(filename, jpg_file_data, content_type="image/jpeg")

        return initial_uploaded_file

    def createProfile(self):
        user = User.objects.create_user(username='testuser', password='testpassword')

        # Create a UserProfile instance with an initial JPEG image
        profile = UserProfile.objects.create(
            user=user,
            name='ТестЮзер',
            photo_w768=self.getPhoto()
        )
        about = UserProfileAbout.objects.create(user_profile=profile, **{
            'birth_date': datetime.date.fromisoformat('1960-02-02'),
            'gender': 1,
            'is_couple': True,
            'has_children': False
        })
        about.set_interests_tags(['гулять'])

        UserProfileRentPreferences.objects.create(user_profile=profile, **{
            'min_budget': 1000,
            'max_budget': 2000
        })

        return profile

    def tearDown(self):
        self.profile.delete()

    def test_profile_update_valid(self):
        def check(data):
            serializer = UserProfileWithParametersCreateUpdateSerializer(instance=self.profile, data=data, partial=True)
            self.assertTrue(serializer.is_valid().is_all_valid)
            serializer.save()

        def get_profile():
            return UserProfile.objects.get(pk=self.profile.pk)

        data1 = {
            'profile': {
                'name': 'Ульяночка'
            }
        }
        check(data1)
        self.assertEqual(get_profile().name, 'Ульяночка')

        data2 = {
            'profile': {
                'photo': self.getPhoto('valid-format-copy.jpg')
            }
        }
        check(data2)
        self.assertIn(
            'valid-format-copy',
            get_profile().photo_w768.name.split('.')[0]
        )

        data3 = {
            'about': {
                'gender': 2
            }
        }
        check(data3)
        self.assertEqual(get_profile().about.gender, 2)

        data4 = {
            'about': {
                'smoking_level': 1
            }
        }
        check(data4)
        self.assertEqual(get_profile().about.smoking_level, 1)

        data5 = {
            'about': {
                'smoking_level': 3,
                'smokes_cigs': True
            }
        }
        check(data5)
        self.assertEqual(get_profile().about.smoking_level, 3)
        self.assertTrue(get_profile().about.smokes_cigs)

        data6a = {
            'about': {
                'interests': ['плавання', 'дрочка']
            }
        }
        check(data6a)
        self.assertSetEqual(
            set(tag.name for tag in get_profile().about.interests_tags.all()),
            {'плавання', 'дрочка'}
        )

        data6b = {
            'about': {
                'interests': ['ааа', 'бааа']
            }
        }
        check(data6b)
        self.assertSetEqual(
            set(tag.name for tag in get_profile().about.interests_tags.all()),
            {'ааа', 'бааа'}
        )

        data7 = {
            'rent_preferences': {
                'min_budget': 2000,
                'max_budget': 3000
            }
        }
        check(data7)
        self.assertEqual(get_profile().rent_preferences.min_budget, 2000)
        self.assertEqual(get_profile().rent_preferences.max_budget, 3000)

        data8a = {
            'rent_preferences': {
                'locations': ['UA01']
            }
        }
        check(data8a)
        self.assertSetEqual(
            set(loc.hierarchy for loc in get_profile().rent_preferences.locations.all()),
            {'UA01'}
        )

        data8b = {
            'rent_preferences': {
                'locations': ['UA05']
            }
        }
        check(data8b)
        self.assertSetEqual(
            set(loc.hierarchy for loc in get_profile().rent_preferences.locations.all()),
            {'UA05'}
        )

    def test_profile_update_invalid(self):
        def check(data):
            serializer = UserProfileWithParametersCreateUpdateSerializer(instance=self.profile, data=data, partial=True)
            self.assertFalse(serializer.is_valid().is_all_valid)
            return serializer

        data_invalid_budget = {
            'rent_preferences': {
                'min_budget': 500
            }
        }
        check(data_invalid_budget)

        data_invalid_rent_duration = {
            'rent_preferences': {
                'min_rent_duration_level': 1
            }
        }
        check(data_invalid_rent_duration)

        data_invalid_locations = {
            'rent_preferences': {
                'locations': ['UA', 'UA01']
            }
        }
        check(data_invalid_locations)

        data_invalid_interests_tags = {
            'about': {
                'interests': ['fdsfsd', '45342']
            }
        }
        check(data_invalid_interests_tags)


class UserProfileVisibilitySerializerTestCase(TestCase):
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

    def test_profile_visibility_serializer_valid(self):
        data = {
            'is_hidden': True,
        }

        serializer = UserProfileVisibilityUpdateSerializer(self.profile, data=data)
        self.assertTrue(serializer.is_valid())

        instance = serializer.save()
        self.assertEqual(instance, self.profile)
        self.assertEqual(instance.is_hidden, data['is_hidden'])

    def test_profile_visibility_serializer_empty_value(self):
        data_no_key = {}
        serializer_no_key = UserProfileVisibilityUpdateSerializer(self.profile, data=data_no_key)
        self.assertFalse(serializer_no_key.is_valid())

        data_no_value = {
            'is_hidden': None
        }
        serializer_no_value = UserProfileVisibilityUpdateSerializer(self.profile, data=data_no_value)
        self.assertFalse(serializer_no_value.is_valid())
