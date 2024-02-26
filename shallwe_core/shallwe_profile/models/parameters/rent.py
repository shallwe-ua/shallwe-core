from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, IntegrityError
from django.db.models import QuerySet

from shallwe_locations.models import Location
from shallwe_util.efficiency import time_measure
from .choices import RentDurationChoices, RoomSharingChoices
from .. import UserProfile


PROFILE_MAX_BUDGET = settings.PROFILE_MAX_BUDGET


class OverlappingLocationsError(ValidationError):
    pass


def validate_locations_no_overlap(locations: QuerySet[Location]):
    if locations.count() > 1:
        for new_location in locations:
            other_locations = locations.exclude(pk=new_location.pk)  # Excluding the one checked against
            for other_new_location in other_locations:
                if (new_location.hierarchy.startswith(other_new_location.hierarchy)
                        or other_new_location.hierarchy.startswith(new_location.hierarchy)):
                    raise OverlappingLocationsError(f"Violation of hierarchical add logic:"
                                                    f" {new_location.search_name}"
                                                    f" {new_location.hierarchy}"
                                                    f" overlaps with {other_new_location.search_name}"
                                                    f" {other_new_location.hierarchy}")


class MinBudgetGTMaxBudgetError(ValidationError):
    pass


class UserProfileRentPreferences(models.Model):
    """**Caution:**\n
    Do NOT use locations manager to manage locations.\n
    Instead, pass new set of locations to set_locations method"""

    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        null=False,
        related_name='rent_preferences'
    )

    # Budget
    min_budget = models.PositiveIntegerField(
        null=False,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(PROFILE_MAX_BUDGET),
        ]
    )
    max_budget = models.PositiveIntegerField(
        null=False,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(PROFILE_MAX_BUDGET),
        ]
    )
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

    locations = models.ManyToManyField(
        Location,
        through='UserProfilePreferredLocations',
        related_name='preferred_in'
    )

    class Meta:
        constraints = [
            # Budget
            models.CheckConstraint(
                check=models.Q(min_budget__lte=models.F('max_budget')),
                name='rent-prefs-min_budget-lte-max_budget',
                violation_error_message='min_budget should be less than or equal to max_budget.'
            ),
            models.CheckConstraint(
                check=models.Q(min_budget__gte=0) & models.Q(min_budget__lte=PROFILE_MAX_BUDGET),
                name='rent-prefs-min_budget-range',
                violation_error_message=f'min_budget should be within the range [0, {PROFILE_MAX_BUDGET}].'
            ),
            models.CheckConstraint(
                check=models.Q(max_budget__gte=0) & models.Q(max_budget__lte=PROFILE_MAX_BUDGET),
                name='rent-prefs-max_budget-range',
                violation_error_message=f'max_budget should be within the range [0, {PROFILE_MAX_BUDGET}].'
            ),
            # Rent duration
            models.CheckConstraint(
                check=models.Q(max_rent_duration_level__gte=models.F('min_rent_duration_level')),
                name='rent-prefs-max_rent_duration-gte-min_rent_duration',
                violation_error_message='max_rent_duration_level should be greater than or equal to min_rent_duration_level.'
            ),
        ]

    def __init__(self, *args, **kwargs):
        self._validate_init_values(kwargs)
        super().__init__(*args, **kwargs)

    def _validate_init_values(self, kwargs):
        provided_min_rent_duration = kwargs.get('min_rent_duration_level')
        provided_max_rent_duration = kwargs.get('max_rent_duration_level')

        if (any((provided_min_rent_duration, provided_max_rent_duration))
                and not all((provided_min_rent_duration, provided_max_rent_duration))):
            raise ValidationError('Both rent_duration levels should be provided or neither')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_locations()

    # Todo: ought to be refactored along with About related tags setters. same structure in general. DRY
    def set_locations(self, locations: QuerySet[Location] = None):
        if self.pk:
            if locations:
                validate_locations_no_overlap(locations)
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


class UserProfilePreferredLocations(models.Model):
    related_preferences = models.ForeignKey(UserProfileRentPreferences, on_delete=models.CASCADE, null=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('related_preferences', 'location')


if settings.SHALLWE_CONF_ENV_MODE == 'DEV':
    validate_locations_no_overlap = time_measure(
        validate_locations_no_overlap
    )
