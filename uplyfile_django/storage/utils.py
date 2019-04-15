from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from unidecode import unidecode


def get_setting(name, fallback=None):
    uplyfile_storage = getattr(settings, "UPLYFILE_STORAGE", {})
    try:
        return uplyfile_storage[name]
    except KeyError:
        fallback()


def not_found(name):
    def raiser():
        raise ImproperlyConfigured(f"Uplyfile's '{name}' config variable isn't set")

    return raiser


def normalize_name(name):
    return unidecode(name)
