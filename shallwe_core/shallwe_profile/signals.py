from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import UserProfile


# Profile
@receiver([post_save, post_delete], sender=UserProfile)
def handle_user_profile_save(sender, instance, **kwargs):
    # Check if the instance has stored old photo paths and delete old photos if so
    if hasattr(instance, '_photo_paths_to_remove') and instance._photo_paths_to_remove:
        instance._delete_old_photos()
