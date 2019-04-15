import json
import os

import pytest

from uplyfile_django.storage.file_to_url_mapper import FileToUrlMapper


@pytest.fixture
def mappings_file(tmp_path):
    file = tmp_path / "map.json"
    file.touch()
    return file


@pytest.fixture
def mappings_file_with_data(tmp_path, mappings_file):
    mappings = {"undertale.sans": "cdn.uplyfile.com/undertale.sans"}
    with open(mappings_file, "w") as f:
        json.dump(mappings, f)

    return mappings_file


@pytest.fixture
def mapper_with_data(mappings_file_with_data):
    return FileToUrlMapper(str(mappings_file_with_data))


@pytest.fixture
def mapper(mappings_file):
    return FileToUrlMapper(str(mappings_file))


class TestFileToUrlMapper:
    def test_without_existing_mappings_file_constructor_uses_empty_one(self, mapper):
        assert mapper.mappings == {}

    def test_save_doesnt_update_mappings_file(self, mapper, mappings_file):
        mapper.save("img.jpg", "someurl/img.jpg")

        assert os.stat(str(mappings_file)).st_size == 0

    def test_with_new_filename_save_creates_new_entry(self, mapper):
        assert mapper.mappings == {}

        mapper.save("somefile", "someurl")

        assert mapper.mappings == {"somefile": "someurl"}

    def test_with_existing_filename_save_updates_old_entry(self, mapper_with_data):
        assert mapper_with_data.mappings != {}

        mapper_with_data.save("undertale.sans", "someurl")

        assert mapper_with_data.mappings == {"undertale.sans": "someurl"}

    def test_calling_get_with_saved_filename_returns_url(self, mapper_with_data):
        assert (
            mapper_with_data.get("undertale.sans") == "cdn.uplyfile.com/undertale.sans"
        )

    def test_calling_get_with_not_saved_filename_raises_key_error(self, mapper):
        non_existent = "not existing filename"
        with pytest.raises(KeyError, match=f".* {non_existent} .*"):
            assert mapper.get(non_existent)
