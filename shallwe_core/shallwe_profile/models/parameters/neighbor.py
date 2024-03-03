from typing import Collection

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from .choices import GenderChoices, SmokingLevelChoices, NeighbourlinessLevelChoices, GuestsLevelChoices, \
    PartiesLevelChoices, NeatnessLevelChoices, OccupationChoices, DrinkingLevelChoices, BedtimeLevelChoices
from .. import UserProfile


# Todo: actually all this stuff probably belongs more to search than profile.
#  I can imagine the product without search and this module - just browsing profiles (on the other hand, you then would
#  like to know what's people's expectations by reading... But not here anyway) Think it through.
class NotUniqueAcceptedItemsError(ValidationError):
    pass


class UserProfileNeighborPreferences(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        null=False,
        related_name='neighbor_preferences'
    )

    # Age
    min_age_accepted = models.PositiveSmallIntegerField(null=False, default=16)
    max_age_accepted = models.PositiveSmallIntegerField(null=False, default=130)
    # ------

    gender_accepted = models.PositiveSmallIntegerField(null=True, blank=True, choices=GenderChoices.choices)
    is_couple_accepted = models.BooleanField(null=True, blank=True)
    are_children_accepted = models.BooleanField(null=True, blank=True)
    occupations_accepted = ArrayField(
        models.PositiveSmallIntegerField(null=False, choices=OccupationChoices.choices),
        null=True,
        blank=True
    )

    drinking_levels_accepted = ArrayField(
        models.PositiveSmallIntegerField(null=False, choices=DrinkingLevelChoices.choices),
        null=True,
        blank=True
    )

    # Smoking
    max_smoking_level_accepted = models.PositiveSmallIntegerField(
        null=False,
        choices=SmokingLevelChoices.choices,
        default=SmokingLevelChoices.EVERYWHERE
    )
    are_nonsmokers_accepted = models.BooleanField(null=False, default=True)
    # ------

    neighbourliness_level_accepted = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=NeighbourlinessLevelChoices.choices
    )
    max_guests_level_accepted = models.PositiveSmallIntegerField(
        null=False,
        choices=GuestsLevelChoices.choices,
        default=GuestsLevelChoices.OFTEN
    )
    max_parties_level_accepted = models.PositiveSmallIntegerField(
        null=True,
        choices=PartiesLevelChoices.choices,
        default=PartiesLevelChoices.OFTEN
    )
    bedtime_levels_accepted = ArrayField(
        models.PositiveSmallIntegerField(null=False, choices=BedtimeLevelChoices.choices),
        null=True,
        blank=True
    )
    neatness_level_accepted = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=NeatnessLevelChoices.choices
    )

    # Animals
    are_cats_accepted = models.BooleanField(null=False, default=True)
    are_dogs_accepted = models.BooleanField(null=False, default=True)
    are_reptiles_accepted = models.BooleanField(null=False, default=True)
    are_birds_accepted = models.BooleanField(null=False, default=True)
    are_other_animals_accepted = models.BooleanField(null=False, default=True)
    # ------

    class Meta:
        constraints = [
            # Age
            models.CheckConstraint(
                check=models.Q(min_age_accepted__gte=16, max_age_accepted__lte=130),
                name='min_age_accepted-between-16-and-130'
            ),
            models.CheckConstraint(
                check=models.Q(min_age_accepted__gte=16, max_age_accepted__lte=130),
                name='max_age_accepted-between-16-and-130'
            ),
            models.CheckConstraint(
                check=models.Q(min_age_accepted__lte=models.F('max_age_accepted')),
                name='min_age_accepted-lte-max_age_accepted'
            ),
            # Smoking
            models.CheckConstraint(
                check=(
                        ~models.Q(max_smoking_level_accepted=SmokingLevelChoices.NO_SMOKING) |
                        models.Q(are_nonsmokers_accepted=True)
                ),
                name='neighbor-prefs-nonsmokers-accepted-if-no-smoking',
                violation_error_message='If maximum smoking level accepted is "No Smoking" (1),'
                                        ' nonsmokers must be accepted'
            )
        ]

    def _set_list_values(self, field_name: str, values: Collection[models.IntegerChoices] = None):
        if values:
            if len(set(values)) != len(values):
                raise NotUniqueAcceptedItemsError(f'{field_name} values should not repeat')
            setattr(self, field_name, values)
        else:
            setattr(self, field_name, [])

    def set_accepted_occupations(self, occupations: list[OccupationChoices] = None):
        self._set_list_values('occupations_accepted', occupations)

    def set_accepted_drinking_levels(self, drinking_levels: list[DrinkingLevelChoices] = None):
        self._set_list_values('drinking_levels_accepted', drinking_levels)

    def set_accepted_bedtime_levels(self, bedtime_levels: list[BedtimeLevelChoices] = None):
        self._set_list_values('bedtime_levels_accepted', bedtime_levels)
