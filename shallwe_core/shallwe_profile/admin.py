from django.contrib import admin
import nested_admin
from django.utils.html import format_html

from .models import UserProfile, UserProfileAbout, UserProfileRentPreferences, UserProfilePreferredLocations


class UserProfileAboutInline(nested_admin.NestedStackedInline):
    model = UserProfileAbout
    extra = 0
    fields = ['birth_date', 'gender', 'is_couple', 'has_children', 'occupation_type',
              'drinking_level', 'smoking_level', 'smokes_iqos', 'smokes_vape', 'smokes_tobacco', 'smokes_cigs',
              'neighbourliness_level', 'guests_level', 'parties_level', 'bedtime_level', 'neatness_level',
              'has_cats', 'has_dogs', 'has_reptiles', 'has_birds', 'other_animals_tags', 'interests_tags', 'bio']
    verbose_name = "About"
    verbose_name_plural = "About"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super(UserProfileAboutInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'other_animals_tags':
            field.label = 'Other Animals'
            field.required = False
        if db_field.name == 'interests_tags':
            field.label = 'Interests'
            field.required = False
        return field


class LocationsInline(nested_admin.NestedTabularInline):
    model = UserProfilePreferredLocations
    extra = 0


class RentPreferencesInline(nested_admin.NestedStackedInline):
    model = UserProfileRentPreferences
    extra = 0
    inlines = [LocationsInline]


class UserProfileAdmin(nested_admin.NestedModelAdmin):
    inlines = [UserProfileAboutInline, RentPreferencesInline]
    list_display = ('user', 'display_photo')
    readonly_fields = ('display_photo', )

    def display_photo(self, obj):
        if obj.photo_w768:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.photo_w768.url)
        return "No photo"

    display_photo.short_description = 'Photo'


admin.site.register(UserProfile, UserProfileAdmin)
