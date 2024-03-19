from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.fields import empty

from shallwe_locations.models import Location
from .common import non_required_char_list_field
from ..models import UserProfileRentPreferences


class UserProfileRentPreferencesSerializer(serializers.ModelSerializer):
    # Locations passed as hierarchies list
    locations = non_required_char_list_field()

    class Meta:
        model = UserProfileRentPreferences
        fields = [
            'min_budget',
            'max_budget',
            'min_rent_duration_level',
            'max_rent_duration_level',
            'room_sharing_level',
            'locations'
        ]

    def validate_locations(self, location_hierarchies: list[str] = None) -> QuerySet[Location]:
        def check_all_exist(locations_):
            nonexistent_hierarchies = set(location_hierarchies) - set(loc.hierarchy for loc in locations_)

            if nonexistent_hierarchies:
                raise serializers.ValidationError(f"Locations with this hierarchies do not exist:\n"
                                                  f"{nonexistent_hierarchies}")

        def check_no_overlap():
            for i, new_location in enumerate(location_hierarchies):
                other_locations = location_hierarchies[:i] + location_hierarchies[i + 1:]
                for other_new_location in other_locations:
                    if (new_location.startswith(other_new_location)
                            or other_new_location.startswith(new_location)):
                        raise serializers.ValidationError(f"Violation of hierarchical add logic:"
                                                          f" {new_location}"
                                                          f" overlaps with"
                                                          f" {other_new_location}")

        if (loc_len := len(location_hierarchies)) > 30:
            raise serializers.ValidationError(f'Too many locations: {loc_len}. The maximum is 30')

        locations = Location.objects.filter(hierarchy__in=location_hierarchies)

        check_all_exist(locations)
        check_no_overlap()

        return locations

    def validate(self, attrs):
        # Same checks for budget and rent duration fields:
        for field_group_name in ('budget', 'rent_duration_level'):
            field_group_values = []
            # Add min/max to a list values if not None
            for prefix in ('min_', 'max_'):
                attr_value = attrs.get(prefix + field_group_name)
                if isinstance(attr_value, int):
                    field_group_values.append(attr_value)

            # Check whether both min/max or neither provided
            if len(field_group_values) == 1:
                raise serializers.ValidationError(
                    f'Both values for {field_group_name} should be provided or neither'
                )

            # Check whether max >= min if both provided
            elif len(field_group_values) == 2:
                if field_group_values[0] > field_group_values[1]:
                    raise serializers.ValidationError(
                        f'min_{field_group_name} must not be greater than max_{field_group_name}'
                    )

        super().validate(attrs)

        return attrs

    def create_or_update_instance(self, instance, validated_data):
        locations_data = validated_data.pop('locations', [])
        rent_preferences = super().update(instance, validated_data) if instance else super().create(validated_data)
        rent_preferences.set_locations(locations_data)
        return rent_preferences

    def update(self, instance, validated_data):
        return self.create_or_update_instance(instance, validated_data)

    def create(self, validated_data):
        return self.create_or_update_instance(None, validated_data)
