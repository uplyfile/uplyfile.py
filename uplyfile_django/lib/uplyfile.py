import datetime
import requests
import hashlib


class Uplyfile:
    """Provide various methods to interact with Uplyfile's API.

    Attributes:
        expiration_time (int): The time after the signature used in a request expires
        priv_key (str): An Uplyfile's API private key
        pub_key (str): An Uplyfile's API public key
    """

    def __init__(
        self,
        private_key,
        public_key,
        base_api_url="https://uplycdn.com/api",
        api_v="v1",
        signature_expiration=60 * 60 * 24,
    ):
        """Create an Uplyfile object with given private and public keys.

        Args:
            private_key (str): An Uplyfile's API private key
            public_key (str): An Uplyfile's API public key
            base_api_url (str): Base API URL used in requests.
                Defaults to `https://uplycdn.com/api`
            api_v (str): An API version
            signature_expiration (int):
                The time after the signature used in a request expires
        """
        if signature_expiration < 0:
            raise ValueError("Expiration time can't have negative value")
        self._api_url = f"{base_api_url.strip('/')}/{api_v}"
        self.expiration_time = signature_expiration
        self.priv_key = private_key
        self.pub_key = public_key

    def get_file_url(self, file):
        raise NotImplementedError

    def upload(self, name, content):
        """Uploads a file with given name to the Uplyfile's API

        Args:
            name (str): A name for the uploaded file
            content (File): The uploaded file
        Returns:
            A Requests library object with API response data
        """
        current_time = datetime.datetime.now(datetime.timezone.utc)
        exp_date = str(current_time.timestamp() + self.expiration_time)
        return requests.post(
            f"{self._api_url}/upload/",
            headers={
                "Uply-Public-Key": self.pub_key,
                "Uply-Expires": exp_date,
                "Uply-Signature": self._gen_signature(exp_date),
            },
            files={"file": (name, content, "image/*")},
            timeout=10,
        )

    def _gen_signature(self, exp_date):
        return hashlib.sha256(f"{self.priv_key}{exp_date}".encode("utf-8")).hexdigest()
