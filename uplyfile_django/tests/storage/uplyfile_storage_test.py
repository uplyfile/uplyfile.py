from io import BytesIO
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.test import override_settings
from requests import HTTPError

from uplyfile_django.storage import UplyfileStorage


@pytest.fixture
def storage(tmp_path):
    return UplyfileStorage(mappings_file=tmp_path / "mappings.json")


def file_url(name):
    return f"https://uplycdn.com/2pL19S/YgrvILCbqdjO/{name}"


class MockedResponse:
    def __init__(self, state=404):
        if state == 404:
            self.status_code = 404
            self.content = "\xde\xad"

        elif state == 200:
            self.status_code = 200
            self.content = "\xca\xfe\xba\xbe"

        elif state == 403:
            self.status_code = 403
            self.json = lambda: {
                "detail": "Authentication credentials were not provided."
            }

    def raise_for_status(self):
        if self.status_code != 200:
            raise HTTPError(f"Status code: {self.status_code}")


class TestStorage:
    @override_settings(UPLYFILE_STORAGE={})
    def test_creating_storage_without_pub_or_secret_keys_should_raise(self):
        with pytest.raises(ImproperlyConfigured):
            UplyfileStorage()

    @override_settings()
    def test_creating_storage_without_UPLYFILE_STORAGE_should_raise(self):
        del settings.UPLYFILE_STORAGE
        with pytest.raises(ImproperlyConfigured):
            UplyfileStorage()

    def test_exists_return_false_when_file_not_mapped(self, storage):
        assert not storage.exists("any_file")

    @patch("uplyfile_django.storage.Uplyfile")
    def test_exists_returns_false_when_file_mapped_but_not_uploaded(
        self, uply_mock, storage
    ):
        uply_mock.file_exists.return_value = False
        storage.uplyfile = uply_mock

        storage.mapper.save("uploaded", "https://uplycdn.com/project/file/file.png")
        assert not storage.exists("uploaded")
        uply_mock.file_exists.assert_called_once()

    @patch("uplyfile_django.storage.Uplyfile")
    def test_exists_returns_true_when_file_mapped_and_hosted(self, uply_mock, storage):
        uply_mock.file_exists.return_value = True
        storage.uplyfile = uply_mock

        storage.mapper.save(
            "polydactyl_cat", "https://uplycdn.com/docs/EEgh6umeTVIg/polydactyl_cat"
        )

        assert storage.exists("polydactyl_cat")
        uply_mock.file_exists.assert_called_once()

    @patch("uplyfile_django.storage.Uplyfile")
    def test_exists_returns_false_when_file_not_mapped(self, uply_mock, storage):
        uply_mock.file_exists.return_value = True
        storage.uplyfile = uply_mock

        assert not storage.exists("polydactyl_cat")
        uply_mock.file_exists.assert_not_called()

    def test_url_returns_url_associated_with_given_name(self, storage):
        storage.mapper.save("some_url", "name")
        assert storage.url("some_url") == "name"

    @patch("uplyfile_django.storage.Uplyfile")
    def test_url_doesnt_query_uply_api(self, mock, storage):
        storage.mapper.save("some_url", "name")
        mock.get_file_url.assert_not_called()

    def test_get_valid_name_removes_all_unicode(self, storage):
        assert storage.get_valid_name("☺☻😃😄😅😆") == ""

    def test_get_valid_name_leaves_name_written_in_ascii(self, storage):
        name = "p_f_@-123_,.<>_/-"
        assert storage.get_valid_name(name) == name


class TestStoreRetrieveFiles:
    @patch("uplyfile_django.storage.Uplyfile")
    def test_saving_new_file_returns_name(self, uply_mock, storage):
        NAME = "example"
        uply_mock.get_file_url.return_value = None
        uply_mock.upload.return_value = file_url(NAME)
        storage.uplyfile = uply_mock

        from_save = storage._save(NAME, BytesIO())
        assert from_save == NAME
        assert storage.exists(NAME)

    @patch("uplyfile_django.storage.Uplyfile")
    def test_saving_by_path_saves_file_with_name_inferred_from_path(
        self, uply_mock, tmp_path, storage
    ):
        NAME = "example"
        uply_mock.get_file_url.return_value = None
        uply_mock.upload.return_value = file_url(NAME)
        storage.uplyfile = uply_mock

        file = tmp_path / NAME
        file.touch()

        from_save = storage.save_by_path(file)
        assert from_save == NAME
        assert storage.exists(NAME)

    def test_opening_not_mapped_file_should_raise(self, tmp_path, storage):

        with pytest.raises(KeyError):
            storage._open(tmp_path / "not_existing")

    @patch.object(UplyfileStorage, "_session")
    def test_opening_mapped_but_not_uplaoded_file_should_raise(self, req_mock, storage):
        NAME = "not_existing"
        req_mock.get.return_value = MockedResponse(state=404)
        storage.mapper.save(NAME, file_url(NAME))

        with pytest.raises(IOError):
            storage._open(NAME)

        req_mock.get.assert_called_once()

    @patch.object(UplyfileStorage, "_session")
    def test_opening_mapped_and_uploaded_file_should_return_content_file(
        self, req_mock, storage
    ):
        NAME = "existing"
        req_mock.get.return_value = MockedResponse(state=200)
        storage.mapper.save(NAME, file_url(NAME))

        f = storage._open(NAME)
        assert isinstance(f, ContentFile)

        req_mock.get.assert_called_once()
