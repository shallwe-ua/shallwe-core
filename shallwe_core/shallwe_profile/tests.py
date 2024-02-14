from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User

from shallwe_locations.models import Location
from .models import UserProfile, UserProfileRentPreferences


# class UserProfileModelTest(TestCase):
#     def setUp(self):
#         from django.contrib.staticfiles import finders
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.jpeg_file_path = finders.find('shallwe_profile/img/valid-format.jpg')
#
#     def test_user_profile_creation(self):
#         # Open the file, read binary data, and create a SimpleUploadedFile
#         with open(self.jpeg_file_path, 'rb') as webp_file:
#             jpg_file_data = webp_file.read()
#             jpeg_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")
#
#         # Create a UserProfile instance with a sample image
#         profile = UserProfile(
#             user=self.user,
#             name='ТестЮзер',
#             photo_w768=jpeg_uploaded_file
#         )
#         # profile.about, profile.rent_preferences, profile.neighbor_preferences = ['mock'] * 3    # Passing related rule
#         profile.save()
#
#         # Assert that the UserProfile instance was created successfully
#         self.assertIsInstance(profile, UserProfile)
#         self.assertEqual(profile.user, self.user)
#         self.assertEqual(profile.name, 'ТестЮзер')
#
#         # Check if dynamically generated images are created
#         self.assertTrue(profile.photo_w540.url)
#         self.assertTrue(profile.photo_w192.url)
#         self.assertTrue(profile.photo_w64.url)
#
#         profile.delete()
#
#     def test_user_profile_photo_change_and_profile_deletion(self):
#         # Open the file, read binary data, and create a SimpleUploadedFile
#         with open(self.jpeg_file_path, 'rb') as jpg_file:
#             jpg_file_data = jpg_file.read()
#             initial_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")
#
#         # Create a UserProfile instance with an initial JPEG image
#         profile = UserProfile.objects.create(
#             user=self.user,
#             name='ТестЮзер',
#             photo_w768=initial_uploaded_file
#         )
#
#         # Store the initial photo paths for testing
#         initial_photo_paths = {
#             'photo_w768': profile.photo_w768.name,
#             'photo_w540': profile.photo_w540.name,
#             'photo_w192': profile.photo_w192.name,
#             'photo_w64': profile.photo_w64.name,
#         }
#
#         # Change the profile photo
#         profile.photo_w768 = initial_uploaded_file
#         profile.save()
#
#         # Check if new photo paths are deleted after the profile deletion
#         new_photo_paths = {
#             'photo_w768': profile.photo_w768.name,
#             'photo_w540': profile.photo_w540.name,
#             'photo_w192': profile.photo_w192.name,
#             'photo_w64': profile.photo_w64.name,
#         }
#
#         # Check if dynamically generated images are created
#         self.assertTrue(profile.photo_w540.url)
#         self.assertTrue(profile.photo_w192.url)
#         self.assertTrue(profile.photo_w64.url)
#
#         # Check if old photo paths are deleted after the photo change
#         for path in initial_photo_paths.values():
#             print(f"Checking if file '{path}' exists after photo change: {default_storage.exists(path)}")
#             self.assertFalse(default_storage.exists(path), f"File '{path}' still exists after photo change.")
#
#         # Delete the user profile
#         profile.delete()
#
#         # Check if new photo paths are deleted after the profile deletion
#         for path in new_photo_paths.values():
#             print(f"Checking if file '{path}' exists after profile deletion: {default_storage.exists(path)}")
#             self.assertFalse(default_storage.exists(path), f"File '{path}' still exists after profile deletion.")


class UserProfileRentPreferencesTestCase(TestCase):
    fixtures = ['shallwe_locations/fixtures/locations_fixture.json']

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

    def test_create_default_instance(self):
        # Create a UserProfileRentPreferences instance with default values
        rent_preferences = UserProfileRentPreferences(
            user_profile=self.profile,
            min_budget=5000,
            max_budget=5000
        )

        # Save the instance to the database
        rent_preferences.save()

        # Retrieve the saved instance from the database
        saved_preferences = UserProfileRentPreferences.objects.get(pk=rent_preferences.pk)

        # Check if the retrieved instance has the expected default values
        self.assertEqual(saved_preferences.min_budget, 5000)
        self.assertEqual(saved_preferences.max_budget, 5000)
        self.assertEqual(saved_preferences.min_rent_duration_level, 1)  # Assuming LT_3_MONTH is the first choice
        self.assertEqual(saved_preferences.max_rent_duration_level, 5)  # Assuming GT_YEAR is the last choice
        self.assertEqual(saved_preferences.room_sharing_level, 2)  # Assuming SHARE is the first choice

        # Check if the default location is added
        default_location = Location.get_all_country()
        self.assertIn(default_location, saved_preferences.locations.all())

        # Check if there are no other locations
        self.assertEqual(saved_preferences.locations.count(), 1)

        # Check if the related UserProfile is set correctly
        self.assertEqual(saved_preferences.user_profile, self.profile)

    def test_add_location(self):
        # Create a UserProfileRentPreferences instance with default values
        rent_preferences = UserProfileRentPreferences(
            user_profile=self.profile,
            min_budget=5000,
            max_budget=5000
        )

        # Save the instance to the database
        rent_preferences.save()

        # Retrieve the saved instance from the database
        saved_preferences = UserProfileRentPreferences.objects.get(pk=rent_preferences.pk)

        locations_to_add = ('UA01', 'UA05')
        saved_preferences.set_locations(locations_to_add)

        locations = saved_preferences.locations.all()

        self.assertEqual(len(locations), 2)
        self.assertEqual(locations[0].hierarchy, 'UA01')

    def tearDown(self):
        self.profile.delete()
