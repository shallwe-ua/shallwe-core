from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import models
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    is_hidden = models.BooleanField(null=False, default=False)
    name = models.CharField(null=False)

    # Highest resolution photo
    photo_w768 = ProcessedImageField(upload_to='profile-photos/',
                                     null=False,
                                     processors=[ResizeToFill(768, 768)],
                                     format='WEBP',
                                     options={'quality': 80})

    # Dynamically generated photo miniatures
    photo_w540 = ImageSpecField(source='photo_w768',
                                processors=[ResizeToFill(540, 540)],
                                format='WEBP',
                                options={'quality': 90})

    photo_w192 = ImageSpecField(source='photo_w768',
                                processors=[ResizeToFill(192, 192)],
                                format='WEBP',
                                options={'quality': 80})

    photo_w64 = ImageSpecField(source='photo_w768',
                               processors=[ResizeToFill(64, 64)],
                               format='WEBP',
                               options={'quality': 80})

    # Related groups of parameters
    # about
    # rent_preferences
    # neighbor_preferences
    # ------

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(name__regex=r'^[а-яА-ЯёЁіІїЇєЄґҐ`]{2,16}$'),
                name='user-profile-name-constraints',
                violation_error_message='Name should be: Cyrillic characters only, no spaces, 2-16 characters'
            ),
        ]

    def save(self, *args, **kwargs):
        # Todo: Ensure link related managers (How if they need the profile to be saved first?)
        self._set_old_photos_for_deletion_if_changed()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Store old photo paths for post-signal usage
        self._set_photo_paths_to_remove(self)
        super().delete(*args, **kwargs)

    def _set_old_photos_for_deletion_if_changed(self):
        # Store old photo paths for post-signal usage if changing the photo
        if self.pk is not None:
            previous_instance = UserProfile.objects.get(pk=self.pk)
            if self.photo_w768 != previous_instance.photo_w768:
                self._set_photo_paths_to_remove(previous_instance)

    def _set_photo_paths_to_remove(self, from_instance: 'UserProfile'):
        self._photo_paths_to_remove = {
            'cache_dir': Path(from_instance.photo_w540.name).parent,
            'photo_w768': from_instance.photo_w768.name,
            'photo_w540': from_instance.photo_w540.name,
            'photo_w192': from_instance.photo_w192.name,
            'photo_w64': from_instance.photo_w64.name,
        }

    def _delete_old_photos(self):
        # Precaution if
        if self._photo_paths_to_remove:
            # Delete previous files
            default_storage.delete(self._photo_paths_to_remove['photo_w768'])
            default_storage.delete(self._photo_paths_to_remove['photo_w540'])
            default_storage.delete(self._photo_paths_to_remove['photo_w192'])
            default_storage.delete(self._photo_paths_to_remove['photo_w64'])
            default_storage.delete(self._photo_paths_to_remove['cache_dir'])
            # Precaution reset
            self._photo_paths_to_remove = {}
