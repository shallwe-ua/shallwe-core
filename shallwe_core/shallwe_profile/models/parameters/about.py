from datetime import date
from typing import Collection

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from taggit.managers import TaggableManager
from taggit.models import TagBase, TaggedItemBase

from .choices import GenderChoices, SmokingLevelChoices, NeighbourlinessLevelChoices, GuestsLevelChoices, \
    PartiesLevelChoices, NeatnessLevelChoices, OccupationChoices, DrinkingLevelChoices, BedtimeLevelChoices
from .. import UserProfile


PROFILE_OTHER_ANIMAL_REGEX = settings.PROFILE_OTHER_ANIMAL_REGEX
PROFILE_INTEREST_REGEX = settings.PROFILE_INTEREST_REGEX


# Todo: lots of almost exactly duplicating code for interests and other animals tags. Refactor later. DRY.
# Other animal tags
class OtherAnimalTag(TagBase):
    name = models.CharField(
        verbose_name="Other Animal Name",
        max_length=32,
        help_text="Enter a Cyrillic animal tag name"
    )

    class Meta:
        verbose_name = "Other Animal Tag"
        verbose_name_plural = "Other Animal Tags"
        constraints = [
            models.CheckConstraint(
                check=models.Q(name__regex=PROFILE_OTHER_ANIMAL_REGEX),
                name='profile-about-other-animal-tag-name-constraint',
                violation_error_message='Other animal tag name must be only Cyrillic chars and hyphens, 2-32 chars'
            )
        ]


class TaggedOtherAnimalItem(TaggedItemBase):
    tag = models.ForeignKey(
        OtherAnimalTag,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_items",
    )
    content_object = models.ForeignKey(
        'UserProfileAbout',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Tagged Other Animal Item"
        verbose_name_plural = "Tagged Other Animal Items"


class OtherAnimalsCountError(ValidationError):
    pass


# Interest tags
class InterestTag(TagBase):
    name = models.CharField(
        verbose_name="Interest Name",
        max_length=32,
        help_text="Enter a Cyrillic interest tag name"
    )

    class Meta:
        verbose_name = "Interest Tag"
        verbose_name_plural = "Interest Tags"
        constraints = [
            models.CheckConstraint(
                check=models.Q(name__regex=PROFILE_INTEREST_REGEX),
                name='profile-about-interest-tag-name-constraint',
                violation_error_message='Interest tag name must be only Cyrillic chars, hyphens and spaces, 2-32 chars'
            )
        ]


class TaggedInterestItem(TaggedItemBase):
    tag = models.ForeignKey(
        InterestTag,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_items",
    )
    content_object = models.ForeignKey(
        'UserProfileAbout',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Tagged Interest Item"
        verbose_name_plural = "Tagged Interest Items"


class InterestsCountError(ValidationError):
    pass


# Birthdate validation
class UserAgeValidationError(ValidationError):
    pass


class UserTooYoungError(UserAgeValidationError):
    pass


class UserTooOldError(UserAgeValidationError):
    pass


# Main model
class UserProfileAbout(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        null=False,
        related_name='about'
    )
    
    # Todo: не вынести ли в профиль это? Логичнее и всё равно пригодится
    creation_date = models.DateField(null=False, auto_now_add=True)  # Reference point for max birth_date validation

    # Todo: GeneratedField для возраста? (а будет ли он обновляться)
    birth_date = models.DateField(null=False)
    gender = models.PositiveSmallIntegerField(null=False, choices=GenderChoices.choices)
    is_couple = models.BooleanField(null=False)
    has_children = models.BooleanField(null=False)
    occupation_type = models.PositiveSmallIntegerField(null=True, blank=True, choices=OccupationChoices.choices)

    drinking_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=DrinkingLevelChoices.choices)

    # Smoking
    smoking_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=SmokingLevelChoices.choices)
    smokes_iqos = models.BooleanField(null=False, default=False)
    smokes_vape = models.BooleanField(null=False, default=False)
    smokes_tobacco = models.BooleanField(null=False, default=False)
    smokes_cigs = models.BooleanField(null=False, default=False)
    # ------

    neighbourliness_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=NeighbourlinessLevelChoices.choices)
    guests_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=GuestsLevelChoices.choices)
    parties_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=PartiesLevelChoices.choices)
    bedtime_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=BedtimeLevelChoices.choices)
    neatness_level = models.PositiveSmallIntegerField(null=True, blank=True, choices=NeatnessLevelChoices.choices)

    # Animals
    has_cats = models.BooleanField(null=False, default=False)
    has_dogs = models.BooleanField(null=False, default=False)
    has_reptiles = models.BooleanField(null=False, default=False)
    has_birds = models.BooleanField(null=False, default=False)
    other_animals_tags = TaggableManager(through=TaggedOtherAnimalItem)
    # ------

    interests_tags = TaggableManager(through=TaggedInterestItem)
    bio = models.CharField(null=True, blank=True, max_length=1024)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(smoking_level__gt=1) &
                    (
                        models.Q(smokes_iqos=True) |
                        models.Q(smokes_vape=True) |
                        models.Q(smokes_tobacco=True) |
                        models.Q(smokes_cigs=True)
                    )
                ) | (
                    ~models.Q(smoking_level__gt=1) &
                    (
                        models.Q(smokes_iqos=False) &
                        models.Q(smokes_vape=False) &
                        models.Q(smokes_tobacco=False) &
                        models.Q(smokes_cigs=False)
                    )
                ),
                name='profile-about-smoking-constraints',
                violation_error_message='Either smoking_level null or =1 and smoking types are all False, '
                                        'or smoking_level >1 and at least one of smoking types is True'
            ),
        ]

    def save(self, *args, **kwargs):
        self._check_birth_date_valid()
        super().save(*args, **kwargs)

    # Todo: unify with similar logic in Rent (setting locations)
    def _set_tags(self, field_name: str, amount_err_class: type, tags: Collection[str] = None):
        tags_manager = getattr(self, field_name)
        if self.pk:
            if tags:
                if len(tags) > 5:
                    raise amount_err_class(f'The maximum amount of {field_name} items is 5')
                tags_manager.set(tags)
            else:
                tags_manager.clear()
        else:
            raise IntegrityError(f'Should save UserProfileAbout before setting related {field_name} items')

    def set_other_animals_tags(self, tags: Collection[str] = None):
        self._set_tags(
            'other_animals_tags',
            OtherAnimalsCountError,
            tags
        )

    def set_interests_tags(self, tags: Collection[str] = None):
        self._set_tags(
            'interests_tags',
            InterestsCountError,
            tags
        )

    def _check_birth_date_valid(self):
        min_birth_date = date.today() - relativedelta(years=16)
        if self.birth_date > min_birth_date:
            raise UserTooYoungError('User cannot be younger than 16')

        if not self.pk:  # First time saving the object
            max_birth_date = date.today() - relativedelta(years=120)
            if self.birth_date < max_birth_date:
                raise UserTooOldError("Birth date cannot be older than 120 years ago from now")
        else:
            max_birth_date = self.creation_date - relativedelta(years=120)
            if self.birth_date < max_birth_date:
                raise UserTooOldError("Birth date cannot be more than 120 years from the creation date")
