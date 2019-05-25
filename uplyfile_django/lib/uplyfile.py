import datetime
import hashlib
import mimetypes

import requests


class Uplyfile:
    """Provide various methods to interact with Uplyfile's API.

    Attributes:
        expiration_time (int): The time after the signature used in a request expires
        secret_key (str): An Uplyfile's API secret_key key
        public_key (str): An Uplyfile's API public key
    """

    def __init__(
        self,
        public_key,
        secret_key,
        base_api_url="https://uplycdn.com/api",
        api_v="v1",
        signature_expiration=60 * 60 * 24,
    ):
        """Create an Uplyfile object with given seckret and public keys.

        Args:
            public_key (str): An Uplyfile's API public key
            secret_key (str): An Uplyfile's API secret key
            base_api_url (str): Base API URL used in requests.
                Defaults to `https://uplycdn.com/api`
            api_v (str): An API version
            signature_expiration (int):
                The time after the signature used in a request expires
        """
        if signature_expiration < 0:
            raise ValueError("Expiration time can't have negative value")
        self._api_url = f"{base_api_url.strip('/')}/{api_v}"
        self._UPLY_ENDPOINTS = {
            "list_project_files": f"{self._api_url}/files/",
            "upload": f"{self._api_url}/upload/",
        }
        self.expiration_time = signature_expiration
        self.secret_key = secret_key
        self.public_key = public_key
        self._cached_project_files_dict = {}

    @property
    def _session(self):
        if not hasattr(self, "_session_obj"):
            self._session_obj = requests.Session()

        return self._session_obj

    def file_exists(self, url):
        """Checks if Uplyfile returns 200 HTTP status code for given URL

        Args:
            url (str): file URL hosted in Uplyfile CDN

        Returns:
            boolean: True if file exists, False otherwise
        """
        response = self._session.head(url)
        return response.status_code == 200

    def get_file_url(self, content, use_cached=True):
        """Gets an URL of uploaded file from Uplyfile API

        Args:
            content (File): A file opened in 'rb' mode

        Returns:
            str: An URL of a file
            None: when matching file couldn't be found
        """
        file_hash = self._md5sum(content)
        if not use_cached or not self._cached_project_files_dict:
            self._cached_project_files_dict = self._group_project_files_by_etag(
                self.list_project_files()
            )

        return (
            self._cached_project_files_dict.get(file_hash, {})
            .get("url", {})
            .get("full")
        )

    def list_project_files(self):
        """List all files from the project

        Returns:
            list: List of files details
        """
        response = self._session.get(
            self._UPLY_ENDPOINTS["list_project_files"],
            headers=self._gen_headers(),
            timeout=10,
        )
        self._handle_api_errors(response.text, response.status_code)
        response.raise_for_status()

        json_data = response.json()
        self._cached_project_files_dict = self._group_project_files_by_etag(json_data)
        return json_data

    def upload(self, name, content):
        """Uploads a file with given name to the Uplyfile's API

        Args:
            name (str): A name for the uploaded file
            content (File): The uploaded file
        Returns:
            A Requests library object with API response data
        """
        response = self._session.post(
            self._UPLY_ENDPOINTS["upload"],
            headers=self._gen_headers(),
            files={"file": (name, content, mimetypes.guess_type(name)[0])},
            timeout=10,
        )
        self._handle_api_errors(response.text, response.status_code)
        response.raise_for_status()
        return response.url

    def _gen_headers(self):
        current_time = datetime.datetime.now(datetime.timezone.utc)
        exp_date = str(current_time.timestamp() + self.expiration_time)
        return {
            "Uply-Public-Key": self.public_key,
            "Uply-Expires": exp_date,
            "Uply-Signature": self._gen_signature(exp_date),
        }

    def _gen_signature(self, exp_date):
        return hashlib.sha256(
            f"{self.secret_key}{exp_date}".encode("utf-8")
        ).hexdigest()

    def _md5sum(self, fp, blocksize=65536):
        if "b" not in fp.mode:
            raise ValueError("Open file in binary mode in order to use this operation")
        _hash = hashlib.md5()
        fp.seek(0)
        for block in iter(lambda: fp.read(blocksize), b""):
            _hash.update(block)
        fp.seek(0)
        return _hash.hexdigest()

    def _handle_api_errors(self, info, status_code):
        if status_code == 403:
            raise AuthException(
                f"Permission denied, check your API keys\n \
                Detailed info: {info}"
            )

    def _group_project_files_by_etag(self, project_files_list):
        return {e["etag"]: e for e in project_files_list}


class AuthException(Exception):
    pass
