import re
from datetime import date

from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from shallwe_core.settings import PROFILE_OTHER_ANIMAL_REGEX, PROFILE_INTEREST_REGEX
from ..models import UserProfileAbout
from .common import non_required_char_list_field


class UserProfileAboutSerializer(serializers.ModelSerializer):
    other_animals = non_required_char_list_field()
    interests = non_required_char_list_field()

    class Meta:
        model = UserProfileAbout
        fields = [
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
            raise serializers.ValidationError('Birth date cannot be later than 16 years ago')

        max_birth_date = date.today() - relativedelta(years=120)
        if birth_date < max_birth_date:
            raise serializers.ValidationError('Birth date cannot be earlier than 120 years ago')

        return birth_date

    def validate(self, attrs):
        # Check the smoking fields constraints
        smoking_level = attrs.get('smoking_level')
        smoking_types = [
            attrs.get(smoking_type)
            for smoking_type
            in ('smokes_iqos', 'smokes_vape', 'smokes_tobacco', 'smokes_cigs')
        ]

        if smoking_level is not None and smoking_level > 1:
            if not any(smoking_types):
                raise serializers.ValidationError(
                    'If smoking_level > 1, at least one smoking type should be True'
                )
        else:
            if any(smoking_types):
                raise serializers.ValidationError(
                    'If smoking_level is null or = 1, all smoking types should be False'
                )

        super().validate(attrs)

        return attrs

    def update_or_create_instance(self, instance, validated_data):
        other_animals_tags_data = validated_data.pop('other_animals', [])
        interests_tags_data = validated_data.pop('interests', [])

        instance = super().update(instance, validated_data) if instance else super().create(validated_data)

        instance.set_other_animals_tags(other_animals_tags_data)
        instance.set_interests_tags(interests_tags_data)

        return instance

    def update(self, instance, validated_data):
        return self.update_or_create_instance(instance, validated_data)

    def create(self, validated_data):
        return self.update_or_create_instance(None, validated_data)
