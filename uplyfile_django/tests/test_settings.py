import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "test_secret"

UPLYFILE_STORAGE = {
    "API_VERSION": "v1",
    "BASE_API_URL": "https://uplycdn.com/api/",
    "MAPPINGS_FILE": os.path.join(BASE_DIR, "mappings.json"),
    "PUBLIC_KEY": os.environ.get("TEST_PUBLIC_KEY", "as"),
    "SECRET_KEY": os.environ.get("TEST_PRIVATE_KEY", "b"),
}

STATICFILES_STORAGE = "uplyfile_django.storage.UplyfileStorage"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "in_mem",
        "TEST": {"NAME": "in_mem_test"},
    }
}

INSTALLED_APPS = ["uplyfile_django"]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO")}
    },
}
