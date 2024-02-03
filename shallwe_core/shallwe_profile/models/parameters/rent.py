# from django.db import models
#
# from shallwe_locations.models import Location
# from .choices import RentDurationChoices, RoomSharingChoices
#
#
# class UserProfileRentPreferences(models.Model):
#     # Todo: try to see bigger picture. How it's used, when it's created, where. Maybe there'll be answers.
#     #  Try lucid schema first on all those activities - see the big picture of process.
#     #  e.g. when user creates a profile, this should happen... when user updates a profile, this should happen...
#     #  and try to think it through step by step and in general
#
#    user_profile = models.OneToOneField(
#         UserProfile,
#         on_delete=models.CASCADE,
#         null=False,
#         related_name='rent_preferences'
#     )
#     # Budget
#     min_budget = models.PositiveSmallIntegerField(null=False)
#     max_budget = models.PositiveSmallIntegerField(null=False)
#     # -----
#
#     # Rent duration
#     min_rent_duration_level = models.PositiveSmallIntegerField(null=False, choices=RentDurationChoices.choices)
#     max_rent_duration_level = models.PositiveSmallIntegerField(null=False, choices=RentDurationChoices.choices)
#     # -----
#
#     room_sharing_level = models.PositiveSmallIntegerField(null=False, choices=RoomSharingChoices.choices)
#
#     locations = models.ManyToManyField(Location, through='UserProfilePreferredLocations', related_name='preferences')
#
#     def set_locations(self, autocodes: tuple[str, ...] = None):
#         if autocodes:
#             for autocode in autocodes:
#                 self._set_location_hierarchically(autocode)
#         else:
#             self._set_default_location()
#
#     def _set_location_hierarchically(self, autocode: str):
#         new_location = Location.objects.get(autocode=autocode)
#         if new_location not in self.locations.all():
#             # Collect overlapping locations to be removed
#             overlapping_locations = [
#                 location
#                 for location in self.locations.all()
#                 if new_location.hierarchy.startswith(
#                     location.hierarchy
#                 ) or location.hierarchy.startswith(
#                     new_location.hierarchy
#                 )
#             ]
#             # Remove overlapping locations in a loop
#             self.locations.remove(*overlapping_locations)
#             self.locations.add(new_location)
#
#     def _set_default_location(self):
#         self.locations.add(Location.get_all_country())
#
#     def save(self, *args, **kwargs):
#         # Set default preferred location if there's no others
#         if not self.locations.exists():
#             self._set_default_location()
#         super().save(*args, **kwargs)
#
#
# class UserProfilePreferredLocations(models.Model):
#     related_preferences = models.ForeignKey(UserProfileRentPreferences, on_delete=models.CASCADE, null=False)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, null=False)
#
#     class Meta:
#         unique_together = ('related_preferences', 'location')
