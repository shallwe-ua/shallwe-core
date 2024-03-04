import re
from collections import OrderedDict

from rest_framework import serializers

from shallwe_core.settings import PROFILE_NAME_REGEX
from shallwe_photo import formatcheck, facecheck
from . import UserProfileRentPreferencesSerializer
from .about import UserProfileAboutSerializer
from ..models import UserProfile


class UserProfileBaseSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(source='photo_w768')  # Renamed field

    class Meta:
        model = UserProfile
        fields = [
            'name',
            'photo',
        ]

    # Todo: make a serializer for photo - also in shallwe_photo
    def validate_photo(self, photo):
        # Check format
        try:
            cleaned_photo = formatcheck.clean_image(photo)
        except formatcheck.ImageValidationError as e:
            raise serializers.ValidationError(str(e))

        # Check face
        is_face_detected = facecheck.check_face_minified_temp(cleaned_photo)
        if not is_face_detected:
            raise serializers.ValidationError('No face found on image')

        return photo

    def validate_name(self, name):
        if not re.match(PROFILE_NAME_REGEX, name):
            raise serializers.ValidationError(
                'Name should be: Cyrillic characters only, no spaces, 2-16 characters'
            )
        return name


class NotValidatedDataSavingError(Exception):
    pass


class UserProfileWithParametersSerializer:
    """
    For the reason I can't quite understand DRF serializers are not equipped to handle writable nested
    serializers if those have nested creation logic themselves.\n\n
    So, in order to do all the stuff we need with all nested parameters we are forced to use multiple serializers
    separately. This class is basically an interface for handling multiple serializers, so we don't do that in views.\n
    Just pass the data from request and kwargs as dict like {'profile': ..., 'rent_preferences': ..., etc...}
    if there are any.
    """

    class ProfileValidationResult:
        def __init__(self, is_profile_valid: bool, is_rent_prefs_valid: bool, is_about_valid: bool):
            self.is_profile_valid = is_profile_valid
            self.is_rent_prefs_valid = is_rent_prefs_valid
            self.is_about_valid = is_about_valid

        def __bool__(self):
            return self.is_all_valid

        @property
        def is_all_valid(self):
            return all((self.is_profile_valid, self.is_rent_prefs_valid, self.is_about_valid))

    def __init__(self, data: dict, kwargs: dict = None):
        kwargs = {} if not kwargs else kwargs

        self.profile_serializer = UserProfileBaseSerializer(
            data=data.get('profile'),
            **kwargs.get('profile', {})
        )
        self.rent_preferences_serializer = UserProfileRentPreferencesSerializer(
            data=data.get('rent_preferences'),
            **kwargs.get('rent_preferences', {})
        )
        self.about_serializer = UserProfileAboutSerializer(
            data=data.get('about'),
            **kwargs.get('about', {})
        )

        self.validation_result = None

    def _get_nested_attr_values(self, attr: str) -> dict:
        result = {}

        for parameter_group in ('profile', 'rent_preferences', 'about'):
            serializer = getattr(self, parameter_group + '_serializer')
            serializer_attr = getattr(serializer, attr)

            if serializer_attr:
                result[parameter_group] = serializer_attr

        return result

    @property
    def data(self):
        return self._get_nested_attr_values('data')

    @property
    def errors(self):
        return self._get_nested_attr_values('errors')

    def get_fields(self):
        fields = OrderedDict({
            'profile': self.profile_serializer.get_fields(),
            'rent_preferences': self.rent_preferences_serializer.get_fields(),
            'about': self.about_serializer.get_fields()
        })
        return fields

    def is_valid(self) -> ProfileValidationResult:
        validation_result = self.ProfileValidationResult(
            self.profile_serializer.is_valid(),
            self.rent_preferences_serializer.is_valid(),
            self.about_serializer.is_valid()
        )

        self.validation_result = validation_result

        return validation_result

    def save(self, kwargs: dict = None) -> UserProfile:
        kwargs = {} if not kwargs else kwargs

        if self.validation_result:
            profile = self.profile_serializer.save(**kwargs.get('profile', {}))

            self.rent_preferences_serializer.save(
                user_profile=profile,
                **kwargs.get('rent_preferences', {})
            )
            self.about_serializer.save(
                user_profile=profile,
                **kwargs.get('about', {})
            )

            return profile
        else:
            raise NotValidatedDataSavingError("Either you didn't validate data before saving or it didn't pass")
