from django.apps import AppConfig


class ShallweProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shallwe_profile'

    def ready(self):
        from . import signals
