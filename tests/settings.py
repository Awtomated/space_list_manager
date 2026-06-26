INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "django_hub",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
HUB_ORGANIZATION_MODEL = "auth.Group"
HUB_GET_ORGANIZATION = "django.contrib.auth.get_user_model"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
