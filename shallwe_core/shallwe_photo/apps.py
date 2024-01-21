from django.apps import AppConfig


class ShallwePhotoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shallwe_photo'

    def ready(self):
        from pi_heif import register_heif_opener
        register_heif_opener()    # for working with HEIF, HEIC
