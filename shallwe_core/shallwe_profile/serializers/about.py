import re
from collections import OrderedDict
from datetime import date

from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from shallwe_core.settings import PROFILE_OTHER_ANIMAL_REGEX, PROFILE_INTEREST_REGEX
from ..models import UserProfileAbout
from .common import non_required_char_list_field, non_required_null_parsing_integer_field, \
    non_required_null_parsing_char_field

ABOUT_FIELDS = [
    'birth_date',
    'gender',
    'is_couple',
    'has_children',
    'occupation_type',
    'drinking_level',
    'smoking_level',
    'smokes_iqos',
    'smokes_vape',
    'smokes_tobacco',
    'smokes_cigs',
    'neighbourliness_level',
    'guests_level',
    'parties_level',
    'bedtime_level',
    'neatness_level',
    'has_cats',
    'has_dogs',
    'has_reptiles',
    'has_birds',
    'other_animals',
    'interests',
    'bio'
]


class UserProfileAboutCreateUpdateSerializer(serializers.ModelSerializer):
    occupation_type = non_required_null_parsing_integer_field()
    drinking_level = non_required_null_parsing_integer_field()
    smoking_level = non_required_null_parsing_integer_field()
    neighbourliness_level = non_required_null_parsing_integer_field()
    guests_level = non_required_null_parsing_integer_field()
    parties_level = non_required_null_parsing_integer_field()
    bedtime_level = non_required_null_parsing_integer_field()
    neatness_level = non_required_null_parsing_integer_field()
    other_animals = non_required_char_list_field()
    interests = non_required_char_list_field()
    bio = non_required_null_parsing_char_field()

    class Meta:
        model = UserProfileAbout
        fields = ABOUT_FIELDS

    def _check_tags(self, attr_name, tags, regex, constraints_message):
        # Check length
        if len(tags) > 5:
            raise serializers.ValidationError(
                f'Maximum amount of {attr_name} tags is 5'
            )

        # Check for uniqueness
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                f'{attr_name} tags should not repeat'
            )

        # Check regex
        for tag in tags:
            if not re.match(regex, tag):
                raise serializers.ValidationError(
                    f'{attr_name} tag must be {constraints_message}'
                )

        return tags

    def validate_other_animals(self, other_animals):
        return self._check_tags(
            'Other animals',
            other_animals,
            PROFILE_OTHER_ANIMAL_REGEX,
            'one UA/RU word and hyphens, 2-32 chars'
        )

    def validate_interests(self, interests):
        return self._check_tags(
            'Interests',
            interests,
            PROFILE_INTEREST_REGEX,
            'UA/RU words, spaces and hyphens, 2-32 chars'
        )

    def validate_birth_date(self, birth_date):
        # Check constraints
        min_birth_date = date.today() - relativedelta(years=16)
        if birth_date > min_birth_date:
            raise serializers.ValidationError('Birth date cannot be less than 16 years ago')

        max_birth_date = date.today() - relativedelta(years=120)
        if birth_date < max_birth_date:
            raise serializers.ValidationError('Birth date cannot be more than 120 years ago')

        return birth_date

    def validate(self, attrs):
        is_updating = self.instance is not None

        # Smoking complex validations
        smoking_types = {'smokes_iqos', 'smokes_vape', 'smokes_tobacco', 'smokes_cigs'}

        # For Update -> calculate resulting values; distinguish between None and not provided
        if is_updating:
            if not (('smoking_level' in attrs) or smoking_types.intersection(attrs)):
                return super().validate(attrs)

            if 'smoking_level' in attrs:
                smoking_level_to_check = attrs.get('smoking_level')
            else:
                smoking_level_to_check = self.instance.smoking_level

            smoking_types_to_check = {}
            # Some types provided - merge with instance values
            if smoking_types.intersection(attrs):
                for smoking_type in smoking_types:
                    smoking_types_to_check[smoking_type] = attrs.get(
                        smoking_type,
                        getattr(self.instance, smoking_type)
                    )
            # No types provided - drop all to False if level = None/1, else use instance values
            else:
                if 'smoking_level' in attrs and (smoking_level_to_check is None or smoking_level_to_check == 1):
                    for smoking_type in smoking_types:
                        smoking_types_to_check[smoking_type] = False
                        attrs[smoking_type] = False
                else:
                    for smoking_type in smoking_types:
                        smoking_types_to_check[smoking_type] = getattr(self.instance, smoking_type)

        # For Create -> collect input values as is; do not distinguish between None and not provided
        else:
            smoking_level_to_check = attrs.get('smoking_level')

            smoking_types_to_check = {}
            for smoking_type in smoking_types:
                smoking_types_to_check[smoking_type] = attrs.get(smoking_type)

        # Validate resulting smoking fields
        is_any_smoken_type_true = any(smoking_types_to_check.values())

        if (smoking_level_to_check is None) or (smoking_level_to_check == 1):
            if is_any_smoken_type_true:
                raise serializers.ValidationError(
                    'If smoking_level is null or = 1, all smoking types should be False'
                )
        else:
            if not is_any_smoken_type_true:
                raise serializers.ValidationError(
                    'If smoking_level > 1, at least one smoking type should be True'
                )

        return super().validate(attrs)

    def create_or_update_instance(self, instance, validated_data):
        other_animals_tags_data = validated_data.pop('other_animals', None)
        interests_tags_data = validated_data.pop('interests', None)

        about = super().update(instance, validated_data) if instance else super().create(validated_data)

        if other_animals_tags_data is not None:
            about.set_other_animals_tags(other_animals_tags_data)
        if interests_tags_data is not None:
            about.set_interests_tags(interests_tags_data)

        return about

    def update(self, instance, validated_data):
        return self.create_or_update_instance(instance, validated_data)

    def create(self, validated_data):
        return self.create_or_update_instance(None, validated_data)


class UserProfileAboutReadSerializer(serializers.ModelSerializer):
    other_animals = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()

    class Meta:
        model = UserProfileAbout
        fields = ABOUT_FIELDS

    def _get_tags_as_list(self, tags_queryset):
        result = list(tags_queryset.values_list('name', flat=True))
        result.sort()
        return result

    def get_other_animals(self, obj):
        return self._get_tags_as_list(obj.other_animals_tags.all())

    def get_interests(self, obj):
        return self._get_tags_as_list(obj.interests_tags.all())

    @property
    def data(self):
        return OrderedDict(super().data)
