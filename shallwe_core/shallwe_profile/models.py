from django.contrib.auth.models import User
from django.db import models

from shallwe_locations.models import Location


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    is_hidden = models.BooleanField(null=False, default=False)
    name = models.CharField(null=False, max_length=16)

    # Photos
    # Todo: see ImageSpecField here https://forum.djangoproject.com/t/override-model-save-method/9555/2
    photo_w768 = models.ImageField(null=False)
    photo_w540 = models.ImageField(null=False)
    photo_w192 = models.ImageField(null=False)
    photo_w64 = models.ImageField(null=False)
    # ------

    # Related groups of parameters
    # about
    # living_preferences
    # neighbor_preferences
    # ------


class UserProfileRelatedParametersGroup(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        null=False,
        related_name='about'
    )

    class Meta:
        abstract = True


class UserProfileLivingPreferences(UserProfileRelatedParametersGroup):
    # Todo: try to see bigger picture. How it's used, when it's created, where. Maybe there'll be answers.
    #  Try lucid schema first on all those activities - see the big picture of process.
    #  e.g. when user creates a profile, this should happen... when user updates a profile, this should happen...
    #  and try to think it through step by step and in general

    # Budget
    min_budget = models.PositiveSmallIntegerField()
    max_budget = models.PositiveSmallIntegerField()
    # -----

    # Rent duration
    min_rent_duration_level = models.PositiveSmallIntegerField()
    max_rent_duration_level = models.PositiveSmallIntegerField()
    # -----

    room_sharing_level = models.PositiveSmallIntegerField()

    locations = models.ManyToManyField(Location, through='UserProfilePreferredLocations', related_name='preferences')

    # Todo: или можно указывать ('00000'), чтобы засетить страну - все остальные по ирерахической логике удалятся
    def set_locations(self, autocodes: tuple[str, ...] = None):
        if autocodes:
            for autocode in autocodes:
                self._set_location_hierarchically(autocode)
        else:
            self._set_default_location()

    def _set_location_hierarchically(self, autocode: str):
        new_location = Location.objects.get(autocode=autocode)
        if new_location not in self.locations.all():
            # Collect overlapping locations to be removed
            overlapping_locations = [
                location
                for location in self.locations.all()
                if new_location.hierarchy.startswith(
                    location.hierarchy
                ) or location.hierarchy.startswith(
                    new_location.hierarchy
                )
            ]
            # Remove overlapping locations in a loop
            self.locations.remove(*overlapping_locations)
            self.locations.add(new_location)

    def _set_default_location(self):
        self.locations.add(Location.get_all_country())

    def save(self, *args, **kwargs):
        # Set default preferred location if there's no others
        if not self.locations.exists():
            self._set_default_location()
        super().save(*args, **kwargs)

    # Todo: МЕЙБИ Сделать функции которые управляют созданием/обновлением профиля -
    #  не в модели методы, а управляющий интерфейс, который содержит всю эту логику ирерах., дефолт и т.д.
    #  или через обджект менеджер это организовать. Тогда мейби интермедиейт таблица не нужна в принципе.


class UserProfilePreferredLocations(models.Model):
    related_preferences = models.ForeignKey(UserProfileLivingPreferences, on_delete=models.CASCADE, null=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('related_preferences', 'location')


class GenderChoices(models.IntegerChoices):
    MALE = 1, 'male'
    FEMALE = 2, 'female'


class OccupationChoices(models.IntegerChoices):
    OFFLINE = 1, 'offline'
    REMOTE = 2, 'remote'
    STUDENT = 3, 'student'
    UNEMPLOYED = 4, 'unemployed'


class DrinkingLevelChoices(models.IntegerChoices):
    NO_DRINKING = 1, 'no'
    ON_SPECIAL_OCCASIONS = 2, 'occasionally'
    ON_WEEKENDS = 3, 'weekends'
    ALWAYS = 4, 'always'


class SmokingLevelChoices(models.IntegerChoices):
    NO_SMOKING = 1, 'no'
    OUTSIDE_APARTMENT = 2, 'outside'
    ON_BALCONY = 3, 'balcony'
    EVERYWHERE = 4, 'everywhere'


class NeighbourlinessLevelChoices(models.IntegerChoices):
    LOW = 1, 'low'
    MODERATE = 2, 'moderate'
    HIGH = 3, 'high'


class GuestsLevelChoices(models.IntegerChoices):
    NO_GUESTS = 1, 'no'
    RARELY = 2, 'rarely'
    OFTEN = 3, 'often'


class PartiesLevelChoices(models.IntegerChoices):
    NO_GUESTS = 1, 'no'
    RARELY = 2, 'rarely'
    OFTEN = 3, 'often'


class BedtimeLevelChoices(models.IntegerChoices):
    EARLY = 1, 'early'
    MIDNIGHT = 2, 'midnight'
    LATE = 3, 'late'
    NO_ROUTINE = 4, 'no'


class NeatnessLevelChoices(models.IntegerChoices):
    LOW = 1, 'low'
    MODERATE = 2, 'moderate'
    HIGH = 3, 'high'


class UserProfileAbout(UserProfileRelatedParametersGroup):
    birth_date = models.DateField(null=False)
    gender = models.PositiveSmallIntegerField(null=False, choices=GenderChoices.choices)
    is_couple = models.BooleanField(null=False)
    has_children = models.BooleanField(null=False)
    occupation_type = models.PositiveSmallIntegerField(null=True, choices=OccupationChoices.choices)

    drinking_level = models.PositiveSmallIntegerField(null=True, choices=DrinkingLevelChoices.choices)

    # Smoking
    smoking_level = models.PositiveSmallIntegerField(null=True, choices=SmokingLevelChoices.choices)
    smokes_iqos = models.BooleanField(null=False, default=False)
    smokes_vape = models.BooleanField(null=False, default=False)
    smokes_tobacco = models.BooleanField(null=False, default=False)
    smokes_cigs = models.BooleanField(null=False, default=False)
    # ------

    neighbourliness_level = models.PositiveSmallIntegerField(null=True, choices=NeighbourlinessLevelChoices.choices)
    guests_level = models.PositiveSmallIntegerField(null=True, choices=GuestsLevelChoices.choices)
    parties_level = models.PositiveSmallIntegerField(null=True, choices=PartiesLevelChoices.choices)
    bedtime_level = models.PositiveSmallIntegerField(null=True, choices=BedtimeLevelChoices.choices)
    neatness_level = models.PositiveSmallIntegerField(null=True, choices=NeatnessLevelChoices.choices)

    # Animals
    has_cats = models.BooleanField(null=False)
    has_dogs = models.BooleanField(null=False, default=False)
    has_reptiles = models.BooleanField(null=False, default=False)
    has_birds = models.BooleanField(null=False, default=False)
    other_animals = models.CharField(null=True, max_length=64)
    # ------

    interests = models.CharField(null=True, max_length=128)
    bio = models.CharField(null=True, max_length=1024)


class UserProfileNeighborPreferences(UserProfileRelatedParametersGroup):
    # Age
    preferred_min_age = models.PositiveSmallIntegerField(null=True)
    preferred_max_age = models.PositiveSmallIntegerField(null=True)
    # ------

    gender = models.PositiveSmallIntegerField(null=True, choices=GenderChoices.choices)
    is_couple = models.BooleanField(null=True)
    has_children = models.BooleanField(null=True)
    # preferred_occupations -> related manager

    drinking_level = models.PositiveSmallIntegerField(null=True, choices=DrinkingLevelChoices.choices)

    # Smoking
    smoking_level = models.PositiveSmallIntegerField(null=True, choices=SmokingLevelChoices.choices)
    smokes_iqos = models.BooleanField(null=False, default=False)
    smokes_vape = models.BooleanField(null=False, default=False)
    smokes_tobacco = models.BooleanField(null=False, default=False)
    smokes_cigs = models.BooleanField(null=False, default=False)
    # ------

    neighbourliness_level = models.PositiveSmallIntegerField(null=True, choices=NeighbourlinessLevelChoices.choices)
    guests_level = models.PositiveSmallIntegerField(null=True, choices=GuestsLevelChoices.choices)
    parties_level = models.PositiveSmallIntegerField(null=True, choices=PartiesLevelChoices.choices)
    bedtime_level = models.PositiveSmallIntegerField(null=True, choices=BedtimeLevelChoices.choices)
    neatness_level = models.PositiveSmallIntegerField(null=True, choices=NeatnessLevelChoices.choices)

    # Animals
    has_cats = models.BooleanField(null=False)
    has_dogs = models.BooleanField(null=False, default=False)
    has_reptiles = models.BooleanField(null=False, default=False)
    has_birds = models.BooleanField(null=False, default=False)
    other_animals = models.CharField(null=True, max_length=64)
    # ------


class UserProfilePreferredOccupation(models.Model):
    related_preferences = models.ForeignKey(UserProfileNeighborPreferences, on_delete=models.CASCADE, related_name='preferred_occupations')
    preferred_occupation = models.PositiveSmallIntegerField(null=True, choices=OccupationChoices.choices)

    class Meta:
        unique_together = ('preferred_about', 'occupation_number')
