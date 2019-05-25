from pathlib import Path
from unittest.mock import patch

import pytest
from requests import HTTPError

from uplyfile_django.lib.uplyfile import AuthException, Uplyfile


def resources_path():
    return Path(__file__).parent.parent / "resources"


@pytest.fixture
def api_keys():
    return ("public_key", "private_key")


@pytest.fixture
def uplyfile(api_keys):
    return Uplyfile(*api_keys)


def test_image(other_name=False):
    img = resources_path() / "sans.webp"
    other_img = resources_path() / "definitely_not_sans.webp"
    return img if not other_name else other_img


def test_image_2():
    return resources_path() / "dog.webp"


def project_files(_):
    return [
        {
            "content_type": "",
            "created": "2019-02-12T16:07:55.384575Z",
            "etag": "cc30f2e1a02160776f14d1718e4967de",
            "file_size_bytes": 7930,
            "is_original_file": True,
            "modified": "2019-02-12T16:07:55.384604Z",
            "operations_string": "",
            "original_name": "sans.webp",
            "project_name": "2pL19S",
            "uid": "YgrvILCbqdjO",
            "url": {
                "base": "https://uplycdn.com/2pL19S/YgrvILCbqdjO",
                "full": "https://uplycdn.com/2pL19S/YgrvILCbqdjO/sans.webp",
                "name": "sans.webp",
                "operational": "https://uplycdn.com/2pL19S/YgrvILCbqdjO/",
            },
            "versions_num": 0,
        }
    ]


class MockedResponse:
    def __init__(self, state=200, json={}, content="", url=""):
        self.content = content
        self.json = lambda: json
        self.status_code = state
        self.url = url

    def raise_for_status(self):
        if self.status_code != 200:
            raise HTTPError(f"Status code: {self.status_code}")

    def text(self):
        return ""


def upload(_, name, content):
    return f"https://uplycdn.com/2pL19S/YgrvILCbqdjO/{name}"


def file_url(name):
    return f"https://uplycdn.com/2pL19S/YgrvILCbqdjO/{name}"


class TestUplyfile:
    def test_negative_timestamp_raises_value_error(self, api_keys):
        with pytest.raises(ValueError):
            Uplyfile(*api_keys, signature_expiration=-1000)

    @patch("uplyfile_django.lib.uplyfile.requests.Session")
    def test_session_is_lazily_instantiated(self, r_mock, api_keys):
        uply = Uplyfile(*api_keys)

        r_mock.assert_not_called()
        uply._session
        r_mock.assert_called_once()
        uply._session
        r_mock.assert_called_once()


class TestUpload:
    @patch.object(Uplyfile, "_session")
    @patch.object(Uplyfile, "list_project_files", project_files)
    def test_given_uploaded_file_filename_get_file_url_returns_url(
        self, session_mock, uplyfile
    ):
        img = test_image()
        with open(str(img), mode="rb") as f:
            session_mock.post.return_value = MockedResponse(
                state=200, url=file_url(img.name)
            )

            uploaded_url = uplyfile.upload(img.name, f)
            url = uplyfile.get_file_url(f)

        assert uploaded_url == url


class TestFileExists:
    @patch.object(Uplyfile, "_session")
    def test_file_exists_uses_head_for_querying(self, session_mock, uplyfile):
        uplyfile.file_exists(file_url("test"))

        session_mock.head.assert_called_once_with(file_url("test"))


class TestGetFileUrl:
    @patch.object(Uplyfile, "list_project_files", project_files)
    @patch.object(Uplyfile, "upload", upload)
    def test_get_file_url_returns_same_link_for_files_with_same_content(self, uplyfile):
        img_1_path = test_image()
        img_2_path = test_image(other_name=True)

        with open(str(img_1_path), "rb") as f:
            uplyfile.upload(img_1_path.name, f)
            uply_url_1 = uplyfile.get_file_url(f)

        with open(str(img_2_path), "rb") as f:
            uplyfile.upload(img_2_path.name, f)
            uply_url_2 = uplyfile.get_file_url(f)

        assert uply_url_1 == uply_url_2

    @patch.object(Uplyfile, "list_project_files", project_files)
    @patch.object(Uplyfile, "upload", upload)
    def test_get_file_url_returns_none_if_file_isnt_uploaded(self, uplyfile):
        with open(str(test_image_2()), "rb") as f:
            uply_url = uplyfile.get_file_url(f)
        assert uply_url is None

    @patch.object(Uplyfile, "list_project_files")
    def test_with_cache_list_project_files_is_called_at_most_once(
        self, project_files_mock, uplyfile
    ):
        with open("uplyfile_django/tests/resources/dog.webp", "rb") as fp:
            project_files_mock.return_value = project_files(self)
            project_files_mock.assert_not_called()

            uplyfile.get_file_url(fp)
            url = uplyfile.get_file_url(fp)

            assert not url
            project_files_mock.assert_called_once()


class TestListProjectFiles:
    @patch.object(Uplyfile, "_session")
    def test_raises_auth_exception_on_403(self, session_mock, uplyfile):
        session_mock.get.return_value = MockedResponse(state=403)
        with pytest.raises(AuthException):
            uplyfile.list_project_files()

    @patch.object(Uplyfile, "_session")
    def test_raises_http_error_on_500(self, session_mock, uplyfile):
        session_mock.get.return_value = MockedResponse(state=500)
        with pytest.raises(HTTPError):
            uplyfile.list_project_files()
