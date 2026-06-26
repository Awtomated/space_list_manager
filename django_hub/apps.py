from django.apps import AppConfig


class DjangoHubConfig(AppConfig):
    name = "django_hub"
    verbose_name = "Django Hub"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from django_hub import conf  # noqa: F401 — triggers validation on startup
