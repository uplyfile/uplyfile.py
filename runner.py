import django
import os
import pytest

os.environ['DJANGO_SETTINGS_MODULE'] = 'uplyfile_django.tests.test_settings'

if __name__ == "__main__":
    django.setup()
    pytest.main()
