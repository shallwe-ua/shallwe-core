import datetime
import json
from collections import OrderedDict

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from shallwe_locations.models import Location
from ...models import UserProfile, UserProfileRentPreferences, UserProfileAbout
from ...serializers import UserProfileRentPreferencesReadSerializer
from ...serializers.about import UserProfileAboutReadSerializer
from ...serializers.profile import UserProfileWithParametersReadSerializer, UserProfileBaseReadSerializer


class UserProfileRentPreferencesReadSerializerTestCase(TestCase):
    fixtures = ['locations_medium_fixture.json']

    def setUp(self):
        self.profile = self.createProfile()
        self.rent_prefs = UserProfileRentPreferences.objects.create(
            user_profile=self.profile,
            min_budget=4000,
            max_budget=5000,
        )
        locations = Location.objects.filter(hierarchy__in=['UA01', 'UA050100100102'])
        self.rent_prefs.set_locations(locations=locations)

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

    def test_default_data_structure_read(self):
        expected_serialization = OrderedDict({
            'min_budget': 4000,
            'max_budget': 5000,
            'min_rent_duration_level': 1,
            'max_rent_duration_level': 5,
            'room_sharing_level': 2,
            'locations': {
                'regions': [
                    {
                        'hierarchy': 'UA01',
                        'region_name': 'АР Крим'
                    },
                ],
                'cities': [
                    {
                        'hierarchy': 'UA0501001001',
                        'ppl_name': 'Вінниця',
                        'districts': [
                            {
                                'hierarchy': 'UA050100100102',
                                'district_name': 'Вінниця-2'
                            }
                        ]
                    }
                ],
                'other_ppls': [],
            }
        })
        serializer = UserProfileRentPreferencesReadSerializer(instance=self.rent_prefs)
        actual_serialization = serializer.data
        self.assertDictEqual(actual_serialization, expected_serialization)
        self.assertEqual(json.dumps(actual_serialization), json.dumps(expected_serialization))  # To check the order


class UserProfileAboutReadSerializerTestCase(TestCase):
    def setUp(self):
        self.profile = self.createProfile()
        self.about = UserProfileAbout.objects.create(
            user_profile=self.profile,
            birth_date=datetime.date.fromisoformat('2002-02-02'),
            gender=1,
            is_couple=True,
            has_children=False
        )
        self.about.set_other_animals_tags(['бобрик', 'крот', 'улітка'])
        self.about.set_interests_tags(['боброведення', 'прокрастинація', 'прогулянки'])

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

    def test_default_data_structure_read(self):
        expected_serialization = OrderedDict({
            'birth_date': '2002-02-02',
            'gender': 1,
            'is_couple': True,
            'has_children': False,
            'occupation_type': None,
            'drinking_level': None,
            'smoking_level': None,
            'smokes_iqos': False,
            'smokes_vape': False,
            'smokes_tobacco': False,
            'smokes_cigs': False,
            'neighbourliness_level': None,
            'guests_level': None,
            'parties_level': None,
            'bedtime_level': None,
            'neatness_level': None,
            'has_cats': False,
            'has_dogs': False,
            'has_reptiles': False,
            'has_birds': False,
            'other_animals': ['бобрик', 'крот', 'улітка'],
            'interests': ['боброведення', 'прогулянки', 'прокрастинація'],
            'bio': None
        })
        serializer = UserProfileAboutReadSerializer(instance=self.about)
        actual_serialization = serializer.data
        self.assertDictEqual(actual_serialization, expected_serialization)
        self.assertEqual(json.dumps(actual_serialization), json.dumps(expected_serialization))  # To check the order


class UserProfileBaseReadSerializerTestCase(TestCase):
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

    def test_basic_profile_serialization(self):
        expected_serialization = OrderedDict([
            ('is_hidden', False),
            ('name', 'ТестЮзер'),
            ('photo_w768', '/media/profile-photos/valid-format.webp'),
            ('photo_w540', '/media/CACHE/images/profile-photos/valid-format/48b30af8f559237f115cb97f6b29d6c3.webp'),
            ('photo_w192', '/media/CACHE/images/profile-photos/valid-format/ffdfdd5001b678517d6f10c82650581a.webp'),
            ('photo_w64', '/media/CACHE/images/profile-photos/valid-format/181eccfd1992d4775c37070e9b98e463.webp')
        ])

        serializer = UserProfileBaseReadSerializer(self.profile)
        actual_serialization = serializer.data

        self.assertDictEqual(expected_serialization, actual_serialization)
        self.assertEqual(json.dumps(expected_serialization), json.dumps(actual_serialization))


class UserProfileWithParametersSerializerReadTestCase(TestCase):
    fixtures = ['locations_mini_fixture.json']

    def setUp(self):
        self.profile = self.createProfile()

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

    def test_base_info_retrieve(self):
        expected_serialization = OrderedDict([('profile',
              OrderedDict([('is_hidden', False),
                           ('name', 'ТестЮзер'),
                           ('photo_w768',
                            '/media/profile-photos/valid-format.webp'),
                           ('photo_w540',
                            '/media/CACHE/images/profile-photos/valid-format/48b30af8f559237f115cb97f6b29d6c3.webp'),
                           ('photo_w192',
                            '/media/CACHE/images/profile-photos/valid-format/ffdfdd5001b678517d6f10c82650581a.webp'),
                           ('photo_w64',
                            '/media/CACHE/images/profile-photos/valid-format/181eccfd1992d4775c37070e9b98e463.webp')])),
             ('rent_preferences',
              OrderedDict([('min_budget', 1000),
                           ('max_budget', 2000),
                           ('min_rent_duration_level', 1),
                           ('max_rent_duration_level', 5),
                           ('room_sharing_level', 2),
                           ('locations',
                            OrderedDict([('regions', []),
                                         ('cities', []),
                                         ('other_ppls', [])]))])),
             ('about',
              OrderedDict([('birth_date', '1960-02-02'),
                           ('gender', 1),
                           ('is_couple', True),
                           ('has_children', False),
                           ('occupation_type', None),
                           ('drinking_level', None),
                           ('smoking_level', None),
                           ('smokes_iqos', False),
                           ('smokes_vape', False),
                           ('smokes_tobacco', False),
                           ('smokes_cigs', False),
                           ('neighbourliness_level', None),
                           ('guests_level', None),
                           ('parties_level', None),
                           ('bedtime_level', None),
                           ('neatness_level', None),
                           ('has_cats', False),
                           ('has_dogs', False),
                           ('has_reptiles', False),
                           ('has_birds', False),
                           ('other_animals', []),
                           ('interests', ['гулять']),
                           ('bio', None)]))])

        serializer = UserProfileWithParametersReadSerializer(instance=self.profile)
        actual_serialization = serializer.data

        self.assertDictEqual(actual_serialization, expected_serialization)
        self.assertEqual(json.dumps(actual_serialization), json.dumps(expected_serialization))
