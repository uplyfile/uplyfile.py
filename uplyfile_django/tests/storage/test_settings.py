import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "test_secret"

UPLYFILE_STORAGE = {
    "API_VERSION": "v1",
    "BASE_API_URL": "https://uplycdn.com/api/",
    "MAPPINGS_FILE": os.path.join(BASE_DIR, "mappings.json"),
    "PUBLIC_KEY": os.environ.get("TEST_PUBLIC_KEY", ""),
    "SECRET_KEY": os.environ.get("TEST_PRIVATE_KEY", ""),
}
