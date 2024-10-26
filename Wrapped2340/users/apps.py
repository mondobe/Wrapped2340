from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Wrapped2340.users'

    def ready(self):
        import Wrapped2340.users.signals