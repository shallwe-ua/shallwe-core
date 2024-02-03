# from django.db import models
#
# from .choices import GenderChoices, SmokingLevelChoices, NeighbourlinessLevelChoices, GuestsLevelChoices, \
#     PartiesLevelChoices, NeatnessLevelChoices, OccupationChoices, DrinkingLevelChoices, BedtimeLevelChoices
#
#
# class UserProfileNeighborPreferences(models.Model):
#    user_profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         null=False,
#         related_name='neighbor_preferences'
#     )

#     # Age
#     min_age_accepted = models.PositiveSmallIntegerField(null=False, default=16)
#     max_age_accepted = models.PositiveSmallIntegerField(null=False, default=130)
#     # ------
#
#     gender_accepted = models.PositiveSmallIntegerField(null=True, choices=GenderChoices.choices)
#     is_couple_accepted = models.BooleanField(null=True)
#     are_children_accepted = models.BooleanField(null=True)
#     # occupations_accepted -> related manager
#
#     # drinking_level_accepted -> related manager
#
#     # Smoking
#     max_smoking_level_accepted = models.PositiveSmallIntegerField(
#         null=False,
#         choices=SmokingLevelChoices.choices,
#         default=SmokingLevelChoices.EVERYWHERE[0]
#     )
#     are_nonsmokers_accepted = models.BooleanField(null=False, default=True)
#     # ------
#
#     neighbourliness_level_accepted = models.PositiveSmallIntegerField(
#         null=True,
#         choices=NeighbourlinessLevelChoices.choices
#     )
#     max_guests_level_accepted = models.PositiveSmallIntegerField(
#         null=False,
#         choices=GuestsLevelChoices.choices,
#         default=GuestsLevelChoices.OFTEN[0]
#     )
#     max_parties_level_accepted = models.PositiveSmallIntegerField(
#         null=True,
#         choices=PartiesLevelChoices.choices,
#         default=PartiesLevelChoices.OFTEN[0]
#     )
#     # bedtime_levels_accepted -> related manager
#     neatness_level_accepted = models.PositiveSmallIntegerField(null=True, choices=NeatnessLevelChoices.choices)
#
#     # Animals
#     are_cats_accepted = models.BooleanField(null=False, default=True)
#     are_dogs_accepted = models.BooleanField(null=False, default=True)
#     are_reptiles_accepted = models.BooleanField(null=False, default=True)
#     are_birds_accepted = models.BooleanField(null=False, default=True)
#     are_other_animals_accepted = models.BooleanField(null=False, default=True)
#     # ------
#
#
# class UserProfileAcceptedOccupation(models.Model):
#     related_preferences = models.ForeignKey(
#         UserProfileNeighborPreferences,
#         on_delete=models.CASCADE,
#         related_name='occupations_accepted'
#     )
#
#     occupation_accepted = models.PositiveSmallIntegerField(null=True, choices=OccupationChoices.choices)
#
#     class Meta:
#         unique_together = ('related_preferences', 'occupation_accepted')
#
#
# class UserProfileAcceptedDrinkingLevel(models.Model):
#     related_preferences = models.ForeignKey(
#         UserProfileNeighborPreferences,
#         on_delete=models.CASCADE,
#         related_name='drinking_levels_accepted'
#     )
#
#     drinking_level_accepted = models.PositiveSmallIntegerField(null=True, choices=DrinkingLevelChoices.choices)
#
#     class Meta:
#         unique_together = ('related_preferences', 'drinking_level_accepted')
#
#
# class UserProfileAcceptedBedtimeLevel(models.Model):
#     related_preferences = models.ForeignKey(
#         UserProfileNeighborPreferences,
#         on_delete=models.CASCADE,
#         related_name='bedtime_levels_accepted'
#     )
#
#     bedtime_level_accepted = models.PositiveSmallIntegerField(null=True, choices=BedtimeLevelChoices.choices)
#
#     class Meta:
#         unique_together = ('related_preferences', 'bedtime_level_accepted')
#
#
# # Todo: многие типы поля повторяются, многие классы повторяются - можно было бы зарефакторить. В будущем.
