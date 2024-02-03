from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        from django.contrib.staticfiles import finders
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.jpeg_file_path = finders.find('shallwe_profile/img/valid-format.jpg')

    def test_user_profile_creation(self):
        # Open the file, read binary data, and create a SimpleUploadedFile
        with open(self.jpeg_file_path, 'rb') as webp_file:
            jpg_file_data = webp_file.read()
            jpeg_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")

        # Create a UserProfile instance with a sample image
        profile = UserProfile(
            user=self.user,
            name='ТестЮзер',
            photo_w768=jpeg_uploaded_file
        )
        # profile.about, profile.rent_preferences, profile.neighbor_preferences = ['mock'] * 3    # Passing related rule
        profile.save()

        # Assert that the UserProfile instance was created successfully
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.name, 'ТестЮзер')

        # Check if dynamically generated images are created
        self.assertTrue(profile.photo_w540.url)
        self.assertTrue(profile.photo_w192.url)
        self.assertTrue(profile.photo_w64.url)

        profile.delete()

    def test_user_profile_photo_change_and_profile_deletion(self):
        # Open the file, read binary data, and create a SimpleUploadedFile
        with open(self.jpeg_file_path, 'rb') as jpg_file:
            jpg_file_data = jpg_file.read()
            initial_uploaded_file = SimpleUploadedFile("valid-format.jpg", jpg_file_data, content_type="image/jpeg")

        # Create a UserProfile instance with an initial JPEG image
        profile = UserProfile.objects.create(
            user=self.user,
            name='ТестЮзер',
            photo_w768=initial_uploaded_file
        )

        # Store the initial photo paths for testing
        initial_photo_paths = {
            'photo_w768': profile.photo_w768.name,
            'photo_w540': profile.photo_w540.name,
            'photo_w192': profile.photo_w192.name,
            'photo_w64': profile.photo_w64.name,
        }

        # Change the profile photo
        profile.photo_w768 = initial_uploaded_file
        profile.save()

        # Check if new photo paths are deleted after the profile deletion
        new_photo_paths = {
            'photo_w768': profile.photo_w768.name,
            'photo_w540': profile.photo_w540.name,
            'photo_w192': profile.photo_w192.name,
            'photo_w64': profile.photo_w64.name,
        }

        # Check if dynamically generated images are created
        self.assertTrue(profile.photo_w540.url)
        self.assertTrue(profile.photo_w192.url)
        self.assertTrue(profile.photo_w64.url)

        # Check if old photo paths are deleted after the photo change
        for path in initial_photo_paths.values():
            print(f"Checking if file '{path}' exists after photo change: {default_storage.exists(path)}")
            self.assertFalse(default_storage.exists(path), f"File '{path}' still exists after photo change.")

        # Delete the user profile
        profile.delete()

        # Check if new photo paths are deleted after the profile deletion
        for path in new_photo_paths.values():
            print(f"Checking if file '{path}' exists after profile deletion: {default_storage.exists(path)}")
            self.assertFalse(default_storage.exists(path), f"File '{path}' still exists after profile deletion.")
