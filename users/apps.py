from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # Loads and registers signal handlers during the app initialization
    def ready(self):
        import users.signals


