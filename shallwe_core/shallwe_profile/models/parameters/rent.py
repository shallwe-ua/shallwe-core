from django.conf import settings
from django.db import models, IntegrityError
from django.db.models import QuerySet

from shallwe_locations.models import Location
from shallwe_util.efficiency import time_measure
from .choices import RentDurationChoices, RoomSharingChoices
from .. import UserProfile


class OverlappingLocationsError(ValueError):
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
            models.CheckConstraint(
                check=models.Q(min_budget__lte=models.F('max_budget')),
                name='rent-prefs-profile-min-budget-lte-max-budget',
                violation_error_message='min_budget should be less than or equal to max_budget.'
            ),
            models.CheckConstraint(
                check=models.Q(min_budget__gte=0) & models.Q(min_budget__lte=99999),
                name='rent-prefs-min-budget-range',
                violation_error_message='min_budget should be within the range [0, 99999].'
            ),
            models.CheckConstraint(
                check=models.Q(max_budget__gte=0) & models.Q(max_budget__lte=99999),
                name='rent-prefs-max-budget-range',
                violation_error_message='max_budget should be within the range [0, 99999].'
            ),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_locations()

    def set_locations(self, hierarchies: tuple[str, ...] = None):
        if self.pk:
            if hierarchies:
                if len(hierarchies) > 1:
                    self._check_no_overlapping_locations(hierarchies)
                locations = Location.objects.filter(hierarchy__in=hierarchies)
                self.locations.set(locations)
            else:
                self._set_default_location()
        else:
            raise IntegrityError('Should save RentPreferences before setting related locations')

    def _ensure_locations(self):
        if not self.locations.exists() or not self.locations.all():
            self._set_default_location()

    def _set_default_location(self):
        self.locations.add(Location.get_all_country())

    def _check_no_overlapping_locations(self, hierarchies: tuple[str, ...]):
        for i, new_hierarchy in enumerate(hierarchies):
            for other_hierarchy in hierarchies[:i] + hierarchies[i+1:]:    # Excluding the current one
                if new_hierarchy.startswith(other_hierarchy) or other_hierarchy.startswith(new_hierarchy):
                    raise OverlappingLocationsError(f"Violation of hierarchical add logic:"
                                                    f" {new_hierarchy}"
                                                    f" overlaps with {other_hierarchy}")


class UserProfilePreferredLocations(models.Model):
    related_preferences = models.ForeignKey(UserProfileRentPreferences, on_delete=models.CASCADE, null=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('related_preferences', 'location')


if settings.SHALLWE_CONF_ENV_MODE == 'DEV':
    UserProfileRentPreferences._check_no_overlapping_locations = time_measure(
        UserProfileRentPreferences._check_no_overlapping_locations
    )
