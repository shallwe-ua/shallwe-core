import re
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from shallwe_core.settings import PROFILE_NAME_REGEX
from shallwe_photo import formatcheck, facecheck
from . import UserProfileRentPreferencesCreateUpdateSerializer, UserProfileRentPreferencesReadSerializer
from .about import UserProfileAboutCreateUpdateSerializer, UserProfileAboutReadSerializer
from ..models import UserProfile


class UserProfileBaseCreateUpdateSerializer(serializers.ModelSerializer):
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


class UserProfileBaseReadSerializer(serializers.ModelSerializer):
    photo_w768 = serializers.ImageField()
    photo_w540 = serializers.ImageField()
    photo_w192 = serializers.ImageField()
    photo_w64 = serializers.ImageField()

    class Meta:
        model = UserProfile
        fields = [
            'is_hidden',
            'name',
            'photo_w768',
            'photo_w540',
            'photo_w192',
            'photo_w64'
        ]

    @property
    def data(self):
        return OrderedDict(super().data)


class NotValidatedDataSavingError(Exception):
    pass


class UserProfileWithParametersCreateUpdateSerializer:
    """
    For the reason I can't quite understand DRF serializers are not equipped to handle writable nested
    serializers if those have nested creation logic themselves.\n

    So, in order to do all the stuff we need with all nested parameters we are forced to use multiple serializers
    separately. This class is basically an interface for handling multiple serializers, so we don't do that in views.\n

    Just pass the data from request and kwargs as dict like {'profile': ..., 'rent_preferences': ..., etc...}
    if there are any.\n
    """

    profile_serializer: UserProfileBaseCreateUpdateSerializer
    rent_preferences_serializer: UserProfileRentPreferencesCreateUpdateSerializer
    about_serializer: UserProfileAboutCreateUpdateSerializer

    class ProfileValidationResult:
        def __init__(self,
                     is_profile_valid: bool = None,
                     is_rent_prefs_valid: bool = None,
                     is_about_valid: bool = None
                     ):
            self.is_profile_valid = is_profile_valid
            self.is_rent_prefs_valid = is_rent_prefs_valid
            self.is_about_valid = is_about_valid

        def __bool__(self):
            return self.is_all_valid

        @property
        def is_all_valid(self):
            return all((
                getattr(self, f'is_{attr_group}_valid') in (True, None)
                for attr_group in ('profile', 'rent_prefs', 'about')
            ))

    def __init__(self, data: dict, kwargs: dict = None, instance: UserProfile = None, partial=False):
        kwargs = {} if not kwargs else kwargs

        self.instance = instance
        self.partial = partial

        for serializer_class, attr_group_name in (
            (UserProfileBaseCreateUpdateSerializer, 'profile'),
            (UserProfileRentPreferencesCreateUpdateSerializer, 'rent_preferences'),
            (UserProfileAboutCreateUpdateSerializer, 'about')
        ):
            kwargs[attr_group_name] = kwargs.get(attr_group_name, {}) | {'partial': partial}

            attr_group_instance = None
            if instance:
                attr_group_instance = instance if attr_group_name == 'profile' else getattr(instance, attr_group_name)

            attr_group_data = data.get(attr_group_name)
            if attr_group_data or not partial:
                serializer = serializer_class(
                    instance=attr_group_instance,
                    data=data.get(attr_group_name),
                    **kwargs.get(attr_group_name)
                )
                setattr(self, f'{attr_group_name}_serializer', serializer)

        self.validation_result = None

    def _get_nested_attr_values(self, attr: str) -> dict:
        result = {}

        for parameter_group in ('profile', 'rent_preferences', 'about'):
            serializer = self._get_serializer(parameter_group)

            if serializer:
                serializer_attr = getattr(serializer, attr)

                if serializer_attr:
                    result[parameter_group] = serializer_attr

        return result

    def _get_serializer(self, attr_group_name: str) -> ModelSerializer:
        try:
            serializer = getattr(self, attr_group_name + '_serializer')
            return serializer
        except AttributeError as err:
            if self.partial:
                pass
            else:
                raise AttributeError(
                    f'No {attr_group_name} serializer was found while instance creation'
                    f' All serializers should`ve been created in this case.'
                ) from err

    @property
    def data(self):
        return self._get_nested_attr_values('data')

    @property
    def errors(self):
        return self._get_nested_attr_values('errors')

    def get_fields(self):
        fields = {}
        for attr_group_name in ('profile', 'rent_preferences', 'about'):
            if serializer := self._get_serializer(attr_group_name):
                fields |= {attr_group_name: serializer.get_fields()}
        fields_ordered = OrderedDict(fields)

        return fields_ordered

    def is_valid(self) -> ProfileValidationResult:
        validation_result_data = {}

        if profile_serializer := self._get_serializer('profile'):
            validation_result_data |= {'is_profile_valid': profile_serializer.is_valid()}
        if about_serializer := self._get_serializer('about'):
            validation_result_data |= {'is_about_valid': about_serializer.is_valid()}
        if rent_prefs_serializer := self._get_serializer('rent_preferences'):
            validation_result_data |= {'is_rent_prefs_valid': rent_prefs_serializer.is_valid()}

        validation_result = self.ProfileValidationResult(**validation_result_data)
        self.validation_result = validation_result

        return validation_result

    def save(self, kwargs: dict = None) -> UserProfile:
        kwargs = {} if not kwargs else kwargs

        if self.validation_result:
            if profile_serializer := self._get_serializer('profile'):
                profile = profile_serializer.save(**kwargs.get('profile', {}))
                profile_arg = {'user_profile': profile} if not self.instance else {}
            else:
                profile = self.instance
                profile_arg = {}

            for attr_group_name in ('about', 'rent_preferences'):
                if serializer := self._get_serializer(attr_group_name):
                    serializer.save(
                        **profile_arg,
                        **kwargs.get(attr_group_name, {})
                    )

            return profile
        else:
            raise NotValidatedDataSavingError("Either you didn't validate data before saving or it didn't pass")


# Todo: Strategy or Template pattern for DRY,
#  but keep them separate to make it more lightweight and easy-readable for GET
class UserProfileWithParametersReadSerializer:
    profile_serializer: UserProfileBaseReadSerializer
    rent_preferences_serializer: UserProfileRentPreferencesReadSerializer
    about_serializer: UserProfileAboutReadSerializer

    def __init__(self, instance: UserProfile = None):
        self.instance = instance

        for serializer_class, attr_group_name in (
            (UserProfileBaseReadSerializer, 'profile'),
            (UserProfileRentPreferencesReadSerializer, 'rent_preferences'),
            (UserProfileAboutReadSerializer, 'about')
        ):
            attr_group_instance = instance if attr_group_name == 'profile' else getattr(instance, attr_group_name)
            serializer = serializer_class(instance=attr_group_instance)
            setattr(self, f'{attr_group_name}_serializer', serializer)

    def _get_nested_attr_values(self, attr: str) -> dict:
        result = OrderedDict()

        for parameter_group in ('profile', 'rent_preferences', 'about'):
            serializer = self._get_serializer(parameter_group)

            if serializer:
                serializer_attr = getattr(serializer, attr)

                if serializer_attr:
                    result[parameter_group] = serializer_attr

        return result

    def _get_serializer(self, attr_group_name: str) -> ModelSerializer:
        serializer = getattr(self, attr_group_name + '_serializer')
        return serializer

    @property
    def data(self):
        return self._get_nested_attr_values('data')
