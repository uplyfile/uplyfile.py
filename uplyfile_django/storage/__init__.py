import pathlib

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from . import utils
from ..lib.uplyfile import Uplyfile
from .file_to_url_mapper import FileToUrlMapper
from .utils import get_setting


@deconstructible
class UplyfileStorage(Storage):
    def __init__(self, mappings_file=None, public_key=None, secret_key=None):
        self.mappings_file_name = mappings_file or get_setting(
            "MAPPINGS_FILE", lambda: "uplyfile.json"
        )
        self.mapper = FileToUrlMapper(self.mappings_file_name)
        self.uplyfile = Uplyfile(
            public_key=public_key
            or get_setting("PUBLIC_KEY", fallback=utils.not_found("PUBLIC_KEY")),
            secret_key=secret_key
            or get_setting("SECRET_KEY", fallback=utils.not_found("SECRET_KEY")),
            api_v=get_setting("API_VERSION", lambda: "v1"),
        )

    @property
    def _session(self):
        if not hasattr(self, "_session_obj"):
            self._session_obj = requests.Session()

        return self._session_obj

    def save_by_path(self, filepath):
        name = pathlib.PurePath(filepath).name
        with open(filepath, "rb") as f:
            return self._save(name, f)

    def _open(self, name, mode="rb"):
        url = self.mapper.get(name)
        response = self._session.get(url, timeout=10)
        if response.status_code == 404:
            raise IOError(f"File {name} isn't uploaded in Uplyfile")
        response.raise_for_status()
        file = ContentFile(response.content)
        file.name = name
        file.mode = mode
        return file

    def _save(self, name, content):
        url = self.uplyfile.get_file_url(content)

        if url is None:
            url = self.uplyfile.upload(name, content)

        self.mapper.save(name, url)
        return name

    def exists(self, name):
        try:
            url = self.mapper.get(name)
        except KeyError:
            return False

        return self.uplyfile.file_exists(url)

    def url(self, name):
        return self.mapper.get(name)

    def get_valid_name(self, name, **kwargs):
        return utils.normalize_name(name)
