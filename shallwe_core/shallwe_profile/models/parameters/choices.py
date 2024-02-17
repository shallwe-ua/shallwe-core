from django.db import models


class RentDurationChoices(models.IntegerChoices):
    LT_3_MONTH = 1, '<3m'
    NEAR_3_MONTH = 2, '3m'
    NEAR_6_MONTH = 3, '6m'
    NEAR_YEAR = 4, 'y'
    GT_YEAR = 5, '>y'


class RoomSharingChoices(models.IntegerChoices):
    NO_SHARE = 1, 'no'
    SHARE = 2, 'yes'
    ONLY_SHARE = 3, 'only'


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
    NEVER = 1, 'no'
    RARELY = 2, 'rarely'
    OFTEN = 3, 'often'


class PartiesLevelChoices(models.IntegerChoices):
    NEVER = 1, 'no'
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

