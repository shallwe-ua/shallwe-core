from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models import QuerySet

from shallwe_locations.models import Location
from shallwe_util.efficiency import time_measure
from .choices import RentDurationChoices, RoomSharingChoices
from .. import UserProfile


class OverlappingLocationsError(ValidationError):
    pass


class UserProfileRentPreferences(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        null=False,
        related_name='rent_preferences'
    )

    # Budget
    min_budget = models.PositiveSmallIntegerField(null=False)
    max_budget = models.PositiveSmallIntegerField(null=False)
    # -----

    # Rent duration
    min_rent_duration_level = models.PositiveSmallIntegerField(
        null=False,
        choices=RentDurationChoices.choices,
        default=RentDurationChoices.LT_3_MONTH
    )
    max_rent_duration_level = models.PositiveSmallIntegerField(
        null=False,
        choices=RentDurationChoices.choices,
        default=RentDurationChoices.GT_YEAR
    )
    # -----

    room_sharing_level = models.PositiveSmallIntegerField(
        null=False,
        choices=RoomSharingChoices.choices,
        default=RoomSharingChoices.SHARE
    )

    locations = models.ManyToManyField(Location, through='UserProfilePreferredLocations', related_name='preferred_in')

    class Meta:
        constraints = [
            # Budget
            models.CheckConstraint(
                check=models.Q(min_budget__lte=models.F('max_budget')),
                name='rent-prefs-min_budget-lte-max_budget',
                violation_error_message='min_budget should be less than or equal to max_budget.'
            ),
            models.CheckConstraint(
                check=models.Q(min_budget__gte=0) & models.Q(min_budget__lte=99999),
                name='rent-prefs-min_budget-range',
                violation_error_message='min_budget should be within the range [0, 99999].'
            ),
            models.CheckConstraint(
                check=models.Q(max_budget__gte=0) & models.Q(max_budget__lte=99999),
                name='rent-prefs-max_budget-range',
                violation_error_message='max_budget should be within the range [0, 99999].'
            ),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_locations()

    # Todo: ought to be refactored along with About related tags setters. same structure in general. DRY
    def set_locations(self, locations: Location | QuerySet[Location] = None):
        if self.pk:
            if locations:
                if len(locations) > 1:
                    self._check_no_overlapping_locations(locations)
                self.locations.set(locations)
            else:
                self._set_default_location()
        else:
            raise IntegrityError('Should save RentPreferences before setting related locations')

    def _ensure_locations(self):
        if not self.locations.exists() or not self.locations.all():
            self._set_default_location()

    def _set_default_location(self):
        self.locations.set((Location.get_all_country(), ))

    def _check_no_overlapping_locations(self, locations: QuerySet[Location]):
        for new_location in locations:
            other_locations = locations.exclude(pk=new_location.pk)  # Excluding the one checked against
            for other_new_location in other_locations:
                if new_location.hierarchy.startswith(other_new_location.hierarchy) or other_new_location.hierarchy.startswith(new_location.hierarchy):
                    raise OverlappingLocationsError(f"Violation of hierarchical add logic:"
                                                    f" {new_location.search_name} {new_location.hierarchy}"
                                                    f" overlaps with {other_new_location.search_name} {other_new_location.hierarchy}")


class UserProfilePreferredLocations(models.Model):
    related_preferences = models.ForeignKey(UserProfileRentPreferences, on_delete=models.CASCADE, null=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('related_preferences', 'location')


if settings.SHALLWE_CONF_ENV_MODE == 'DEV':
    UserProfileRentPreferences._check_no_overlapping_locations = time_measure(
        UserProfileRentPreferences._check_no_overlapping_locations
    )
