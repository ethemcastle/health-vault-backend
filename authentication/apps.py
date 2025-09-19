from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    label = "hv_authentication"

    def ready(self):
        from .signals import ensure_groups
