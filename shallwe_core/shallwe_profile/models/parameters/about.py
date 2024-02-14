# from django.db import models
#
# from .choices import GenderChoices, SmokingLevelChoices, NeighbourlinessLevelChoices, GuestsLevelChoices, \
#     PartiesLevelChoices, NeatnessLevelChoices, OccupationChoices, DrinkingLevelChoices, BedtimeLevelChoices
# from .. import UserProfile
#
#
# class UserProfileAbout(models.Model):
#     user_profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         null=False,
#         related_name='about'
#     )
#
#     birth_date = models.DateField(null=False)
#     gender = models.PositiveSmallIntegerField(null=False, choices=GenderChoices.choices)
#     is_couple = models.BooleanField(null=False)
#     has_children = models.BooleanField(null=False)
#     occupation_type = models.PositiveSmallIntegerField(null=True, choices=OccupationChoices.choices)
#
#     drinking_level = models.PositiveSmallIntegerField(null=True, choices=DrinkingLevelChoices.choices)
#
#     # Smoking
#     smoking_level = models.PositiveSmallIntegerField(null=True, choices=SmokingLevelChoices.choices)
#     smokes_iqos = models.BooleanField(null=False, default=False)
#     smokes_vape = models.BooleanField(null=False, default=False)
#     smokes_tobacco = models.BooleanField(null=False, default=False)
#     smokes_cigs = models.BooleanField(null=False, default=False)
#     # ------
#
#     neighbourliness_level = models.PositiveSmallIntegerField(null=True, choices=NeighbourlinessLevelChoices.choices)
#     guests_level = models.PositiveSmallIntegerField(null=True, choices=GuestsLevelChoices.choices)
#     parties_level = models.PositiveSmallIntegerField(null=True, choices=PartiesLevelChoices.choices)
#     bedtime_level = models.PositiveSmallIntegerField(null=True, choices=BedtimeLevelChoices.choices)
#     neatness_level = models.PositiveSmallIntegerField(null=True, choices=NeatnessLevelChoices.choices)
#
#     # Animals
#     # Todo: mayebe it should be many to many or foreign tables like with some checkbox values in neighbor prefs
#     #  So then we could just simply check for intersection
#     has_cats = models.BooleanField(null=False)
#     has_dogs = models.BooleanField(null=False, default=False)
#     has_reptiles = models.BooleanField(null=False, default=False)
#     has_birds = models.BooleanField(null=False, default=False)
#     other_animals = models.CharField(null=True, max_length=64)
#     # ------
#
#     interests = models.CharField(null=True, max_length=128)
#     bio = models.CharField(null=True, max_length=1024)
