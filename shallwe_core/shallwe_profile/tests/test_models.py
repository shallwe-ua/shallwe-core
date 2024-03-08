from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User

from shallwe_locations.models import Location
from ..models import (UserProfile, UserProfileRentPreferences, UserProfileAbout, OtherAnimalsCountError,
                      InterestsCountError, OtherAnimalTag, InterestTag, UserTooYoungError, UserTooOldError,
                      UserProfileNeighborPreferences, SmokingLevelChoices, GuestsLevelChoices, PartiesLevelChoices,
                      NeatnessLevelChoices, OccupationChoices, BedtimeLevelChoices, DrinkingLevelChoices,
                      RentDurationChoices, RoomSharingChoices, OverlappingLocationsError)


class UserProfileTestCase(TestCase):
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
            name="Мар'ян`ко",
            photo_w768=jpeg_uploaded_file
        )
        # profile.about, profile.rent_preferences, profile.neighbor_preferences = ['mock'] * 3    # Passing related rule
        profile.save()

        # Assert that the UserProfile instance was created successfully
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.name, "Мар'ян`ко")

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


class UserProfileRentPreferencesTestCase(TestCase):
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
        self.assertEqual(saved_preferences.min_rent_duration_level,
                         RentDurationChoices.LT_3_MONTH)  # Assuming LT_3_MONTH is the first choice
        self.assertEqual(saved_preferences.max_rent_duration_level,
                         RentDurationChoices.GT_YEAR)  # Assuming GT_YEAR is the last choice
        self.assertEqual(saved_preferences.room_sharing_level,
                         RoomSharingChoices.SHARE)  # Assuming SHARE is the first choice

        # Check if the default location is added
        default_location = Location.get_all_country()
        self.assertIn(default_location, saved_preferences.locations.all())

        # Check if there are no other locations
        self.assertEqual(saved_preferences.locations.count(), 1)

        # Check if the related UserProfile is set correctly
        self.assertEqual(saved_preferences.user_profile, self.profile)

    def test_invalid_values_creation(self):
        with self.assertRaises(ValidationError):
            rent_preferences = UserProfileRentPreferences(
                user_profile=self.profile,
                min_budget=5000,
                max_budget=5000,
                min_rent_duration_level=1
            )
        with self.assertRaises(ValidationError):
            rent_preferences = UserProfileRentPreferences.objects.create(
                user_profile=self.profile,
                min_budget=5000,
                max_budget=5000,
                min_rent_duration_level=1
            )

    def test_add_location(self):
        rent_preferences = UserProfileRentPreferences.objects.create(
            user_profile=self.profile,
            min_budget=5000,
            max_budget=5000
        )

        # Set invalid locations (overlap)
        with self.assertRaises(OverlappingLocationsError):
            locations_to_add = Location.objects.filter(hierarchy__in=('UA01', 'UA05', 'UA'))
            rent_preferences.set_locations(locations_to_add)

        # Set valid locations
        locations_to_add = Location.objects.filter(hierarchy__in=('UA01', 'UA05'))
        rent_preferences.set_locations(locations_to_add)

        locations = rent_preferences.locations.all()

        self.assertEqual(len(locations), 2)
        self.assertEqual(locations[0].hierarchy, 'UA01')

    def tearDown(self):
        self.profile.delete()


class UserProfileAboutTestCase(TestCase):
    def setUp(self):
        self.profile = self.createProfile()

    def createProfile(self, username: str = 'testuser'):
        from django.contrib.staticfiles import finders
        user = User.objects.create_user(username=username, password='testpassword')
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

    def test_default_values_and_constraints(self):
        about = UserProfileAbout(user_profile=self.profile, birth_date=date(2000, 1, 1), gender=1, is_couple=False,
                                 has_children=False)
        about.save()  # should not raise ValidationError

        # Test constraints
        with self.assertRaises(UserTooYoungError):
            about.birth_date = date.today() - relativedelta(years=15)
            about.save()

    def test_birth_date_validation(self):
        # Test case 1: Birth date is too young
        young_birth_date = date.today() - relativedelta(years=15)
        about = UserProfileAbout(user_profile=self.profile, birth_date=young_birth_date, gender=1, is_couple=False,
                                 has_children=False)
        with self.assertRaises(UserTooYoungError):
            about.save()

        # Test case 2: Birth date is too old (first time saving the object)
        old_birth_date = date.today() - relativedelta(years=121)
        about.birth_date = old_birth_date
        with self.assertRaises(UserTooOldError):
            about.save()

        # Test case 3: Birth date is within valid range
        valid_birth_date = date.today() - relativedelta(years=20)
        about.birth_date = valid_birth_date
        try:
            about.save()
        except ValidationError:
            self.fail("Valid birth date raised ValidationError unexpectedly")

        # Test case 4: Birth date is too old (after first time saving the object)
        old_birth_date = about.creation_date - relativedelta(years=121)
        about.birth_date = old_birth_date
        with self.assertRaises(UserTooOldError):
            about.save()

    def test_set_other_animals_tags(self):
        about = UserProfileAbout.objects.create(user_profile=self.profile, birth_date=date(2000, 1, 1), gender=1,
                                                is_couple=False, has_children=False)
        # Test setting other animals tags
        tags = ('кіт', 'собака', 'миша')
        about.set_other_animals_tags(tags)
        self.assertEqual(about.other_animals_tags.count(), len(tags))

        # Test setting more than 5 tags
        with self.assertRaises(OtherAnimalsCountError):
            about.set_other_animals_tags(('кіт', 'собака', 'миша', 'яструб', 'черепаха', 'тигр'))

    def test_set_interests_tags(self):
        about = UserProfileAbout.objects.create(user_profile=self.profile, birth_date=date(2000, 1, 1), gender=1,
                                                is_couple=False, has_children=False)
        # Test setting interests tags
        tags = ('кіно', 'прогулки', 'срачі')
        about.set_interests_tags(tags)
        self.assertEqual(about.interests_tags.count(), len(tags))

        # Test setting more than 5 tags
        with self.assertRaises(InterestsCountError):
            about.set_interests_tags(('кіно', 'прогулки', 'срачі', 'порно', 'інтернет', 'двач'))

    def test_duplicate_tags_creation(self):
        # Create two UserProfileAbout instances with the same tag names
        about1 = UserProfileAbout.objects.create(user_profile=self.createProfile('user1'), birth_date=date(2000, 1, 1),
                                                 gender=1,
                                                 is_couple=False, has_children=False)
        about2 = UserProfileAbout.objects.create(user_profile=self.createProfile('user2'), birth_date=date(2000, 1, 1),
                                                 gender=1,
                                                 is_couple=False, has_children=False)
        tags = ('кіт', 'собака', 'миша')
        about1.set_other_animals_tags(tags)
        about2.set_other_animals_tags(tags)

        # Check that only one of each tag instance is created in the database
        self.assertEqual(OtherAnimalTag.objects.count(), len(tags))

        # Create another UserProfileAbout instance with the same tag names
        about3 = UserProfileAbout.objects.create(user_profile=self.createProfile('user3'), birth_date=date(2000, 1, 1),
                                                 gender=1,
                                                 is_couple=False, has_children=False)
        about3.set_other_animals_tags(tags)

        # Check that only one of each tag instance is still created in the database
        self.assertEqual(OtherAnimalTag.objects.count(), len(tags))

        # Repeat the same process for interests tags
        about4 = UserProfileAbout.objects.create(user_profile=self.createProfile('user4'), birth_date=date(2000, 1, 1),
                                                 gender=1,
                                                 is_couple=False, has_children=False)
        about5 = UserProfileAbout.objects.create(user_profile=self.createProfile('user5'), birth_date=date(2000, 1, 1),
                                                 gender=1,
                                                 is_couple=False, has_children=False)
        interests = ('кіно', 'прогулки', 'срачі')
        about4.set_interests_tags(interests)
        about5.set_interests_tags(interests)

        # Check that only one of each tag instance is created in the database
        self.assertEqual(InterestTag.objects.count(), len(interests))

        about6 = UserProfileAbout.objects.create(user_profile=self.createProfile('user6'), birth_date=date(2000, 1, 1),
                                                 gender=1,
                                                 is_couple=False, has_children=False)
        about6.set_interests_tags(interests)

        # Check that only one of each tag instance is still created in the database
        self.assertEqual(InterestTag.objects.count(), len(interests))

        for about in about1, about2, about3, about4, about5, about6:
            about.user_profile.delete()

    def tearDown(self):
        self.profile.delete()


class UserProfileNeighborPreferencesTest(TestCase):
    def setUp(self):
        self.profile = self.createProfile()

    def createProfile(self, username: str = 'testuser'):
        from django.contrib.staticfiles import finders
        user = User.objects.create_user(username=username, password='testpassword')
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

    def createNeighborPreferences(self, **kwargs) -> UserProfileNeighborPreferences:
        defaults = {
            'user_profile': self.profile,
        }
        kwargs.update(defaults)
        return UserProfileNeighborPreferences.objects.create(**kwargs)

    def test_defaults_and_nulls(self):
        neighbor_preferences = self.createNeighborPreferences()

        self.assertEqual(neighbor_preferences.min_age_accepted, 16)
        self.assertEqual(neighbor_preferences.max_age_accepted, 130)
        self.assertEqual(neighbor_preferences.max_smoking_level_accepted, SmokingLevelChoices.EVERYWHERE)
        self.assertTrue(neighbor_preferences.are_nonsmokers_accepted)
        self.assertTrue(neighbor_preferences.are_cats_accepted)
        self.assertTrue(neighbor_preferences.are_dogs_accepted)
        self.assertTrue(neighbor_preferences.are_reptiles_accepted)
        self.assertTrue(neighbor_preferences.are_birds_accepted)
        self.assertTrue(neighbor_preferences.are_other_animals_accepted)
        self.assertIsNone(neighbor_preferences.neighbourliness_level_accepted)
        self.assertIsNone(neighbor_preferences.gender_accepted)
        self.assertIsNone(neighbor_preferences.is_couple_accepted)
        self.assertIsNone(neighbor_preferences.are_children_accepted)
        self.assertIsNone(neighbor_preferences.neatness_level_accepted)
        self.assertIsNone(neighbor_preferences.drinking_levels_accepted)
        self.assertIsNone(neighbor_preferences.occupations_accepted)
        self.assertIsNone(neighbor_preferences.bedtime_levels_accepted)
        self.assertEqual(neighbor_preferences.max_guests_level_accepted, GuestsLevelChoices.OFTEN)
        self.assertEqual(neighbor_preferences.max_parties_level_accepted, PartiesLevelChoices.OFTEN)

    def test_user_profile_neighbor_preferences_creation(self):
        try:
            self.createNeighborPreferences(
                min_age_accepted=20,
                max_age_accepted=50,
                max_smoking_level_accepted=SmokingLevelChoices.NO_SMOKING,
                are_nonsmokers_accepted=True,
                max_guests_level_accepted=GuestsLevelChoices.RARELY,
                max_parties_level_accepted=PartiesLevelChoices.NEVER,
                neatness_level_accepted=NeatnessLevelChoices.MODERATE,
                are_cats_accepted=True,
                are_dogs_accepted=False,
                are_reptiles_accepted=True,
                are_birds_accepted=False,
                are_other_animals_accepted=True
            )
        except Exception as e:
            self.fail(f"Valid values for neighbor prefs ended up in Error: {str(e)}")

    def test_accepted_array_items_creation(self):
        neighbor_prefs = self.createNeighborPreferences()

        neighbor_prefs.set_accepted_occupations([OccupationChoices.STUDENT, OccupationChoices.OFFLINE])
        self.assertEqual(len(neighbor_prefs.occupations_accepted), 2)

        neighbor_prefs.set_accepted_bedtime_levels([BedtimeLevelChoices.LATE, BedtimeLevelChoices.MIDNIGHT])
        self.assertEqual(len(neighbor_prefs.bedtime_levels_accepted), 2)

        neighbor_prefs.set_accepted_drinking_levels(
            [DrinkingLevelChoices.NO_DRINKING, DrinkingLevelChoices.ON_SPECIAL_OCCASIONS])
        self.assertEqual(len(neighbor_prefs.drinking_levels_accepted), 2)

        try:
            neighbor_prefs.save()
        except ValidationError:
            self.fail('Got an error trying to save a valid neighbor preferences')

    def tearDown(self):
        self.profile.delete()
