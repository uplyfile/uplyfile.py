import pytest
import io
from PIL import Image
from uplyfile_django.lib.uplyfile import Uplyfile


@pytest.fixture
def api_keys():
    return ("", "")


@pytest.fixture
def test_image():
    file = io.BytesIO()
    image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
    image.save(file, "png")

    return "testfile.png", file


@pytest.fixture
def uplyfile(api_keys):
    return Uplyfile(api_keys)


class TestUplyfile:
    def test_negative_timestamp_raises_value_error(self, api_keys):
        with pytest.raises(ValueError):
            Uplyfile(*api_keys, signature_expiration=-1000)
