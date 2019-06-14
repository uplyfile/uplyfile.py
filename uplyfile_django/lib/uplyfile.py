import os
import re
import datetime
import hashlib
import mimetypes
import requests
from urllib.parse import urlparse


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


class UplyImage:
    """
    The UplyImage class gives the ability to create Uplyfile URLs.

    All operations are possible to use as the chainable with the exception
    of AI Operations that are described below.
    """

    EXPLICIT_VALUES = ("VERY_LIKELY", "LIKELY", "POSSIBLE")

    def __init__(self, path):
        """
        Creates an UplyImage object with given path to the image.

        Argument:
            path - url of the image uploaded to Uplyfile API.

        Variables:
            base_url - url of image from https:// to /image_id/,
            file_name - the name of the image with extension, if it exists,
            operation - the list of operations used on the image.
        """
        self.path = path
        self.base_url, self.file_name = path.rsplit("/", 1)
        self._raise_if_invalid_url(path)
        self._remove_operations_from_url(path)
        self.file_name_without_extension, self.extension = os.path.splitext(
            self.file_name
        )
        self.operation = []

    @property
    def _session(self):
        if not hasattr(self, "_session_obj"):
            self._session_obj = requests.Session()
        return self._session_obj

    def _raise_if_invalid_url(self, path):
        parse = urlparse(path)
        _proper_filepath_regexp = re.compile(r"^/\w+/\w+/")
        if not _proper_filepath_regexp.search(parse.path):
            raise ValueError("Please enter correct path.")

    def _remove_operations_from_url(self, path):
        parse = urlparse(path)
        _proper_filepath_regexp = re.compile(r"^/\w+/\w+/")
        start, stop = _proper_filepath_regexp.search(parse.path).span()
        self.base_url = f"{parse.scheme}://{parse.netloc}" + parse.path[start:stop]

    def _json_load_from_url(self, base_url):
        open_url = self._session.get(f"{base_url}?metadata=extra")
        return open_url.json()

    # FACES
    def avatar(self, size=None):
        """
        Uses 'avatar' operation on the image.

        Operation automatically generates avatar from image.

        Arg:
            size - a number of pixels that sets the value of the height
            and width of the creating avatar.
        """
        operation = "avatar"
        if size is not None:
            operation += f":{size}"
        self.operation.append(operation)
        return self

    def face_mark(self):
        """
        Uses 'face_mark' operation on the image.

        Operation automatically visually marks face on the picture
        which can be later used for 'face_crop'.
        """
        self.operation.append("face_mark")
        return self

    def face_crop(self, face_index=None, align=False):
        """
        Uses 'face_crop' operation on the image.

        Operation crop out the face from the image. Optionally the operation
        is able to crop a selected face and automatically rotate the cropped image
        so the eyes are on the same horizontal line.

        Args:
            face_index - a number of the selected face,
            align - the keyword which activates an align of face
        """
        operation = "face_crop"
        if face_index is not None:
            operation += f":{face_index}"
        if align:
            operation += ":align"
        self.operation.append(operation)
        return self

    # FILE OPTIONS
    def autoformat(self):
        """
        Uses 'autoformat' operation on the image.

        Operation automatically detects what kind of content is supported
        by the client based on 'Accept' http header.
        """
        self.operation.append("autoformat")
        return self

    def download(self):
        """
        Uses 'download' operation on the image.

        Operation causes the Image won't be previewed in a browser as it happens
        by default but will be downloaded.
        """
        self.operation.append("download")
        return self

    def quality(self, value):
        """
        Uses 'quality' operation on the image.

        Operation changes the quality of an output image. Takes 1 argument which
        is either a number or a keyword. Specifying a value is required.

        Arg:
            value - a number between 1 and 100 (the higher the better quality and bigger size)
            or one of the keywords: lightest, light, normal, high, highest.
        """
        operation = "quality"
        if value is not None:
            operation += f":{value}"
        else:
            raise ValueError("Quality requires a value")
        self.operation.append(operation)
        return self

    def progressive(self):
        """
        Uses 'progressive' operation on the image.

        Operation provides a progressive loading of the 'jpg' and 'jpeg' images.
        """
        self.operation.append("progressive")
        return self

    # FILTERS
    def blur(self, strength=None):
        """
        Uses 'blur' operation on the image.

        Operation applies Gaussian blur to the image. Specifying a strength is not required.
        When a method has no argument then 'blur' takes the default value of 'strength'.

        Arg:
            strength - a number greater than or equal to zero, where zero changes nothing.
        """
        operation = "blur"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def median(self, strength=None):
        """
        Uses 'median' operation on the image.

        Operation reduces a 'salt-pepper' type of noise in images taken with high ISO settings.
        Specifying a strength is not required. When a method has no argument then 'median' takes
        the default value of 'strength'.

        Arg:
            strength - a number greater than or equal to zero, where zero changes nothing.
        """
        operation = "median"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def bilateral(self, strength=None):
        """
        Uses 'bilateral' operation on the image.

        Operation works in a similar way to blur, but bilateral also preserves edges.
        Specifying a strength is not required. When a method has no argument then 'bilateral' takes
        the default value of 'strength'.

        Arg:
            strength - a number greater than or equal to zero, where zero changes nothing.
        """
        operation = "bilateral"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def sharpen(self, strength=None):
        """
        Uses 'sharpen' operation on the image.

        Operation provides the sharpening of the image. Specifying a strength is not required.
        When a method has no argument then 'sharpen' takes the default value of 'strength'.

        Arg:
            strength - a number greater than or equal to zero, where zero changes nothing.
        """
        operation = "sharpen"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def autocontrast(self, strength=None):
        """
        Uses 'autocontrast' operation on the image.

        Operation provides the automatically adjusts contrast in the image. Specifying a strength
        is not required. When a method has no argument then 'autocontrast' takes the default value of 'strength'.

        Arg:
            strength - a number greater than or equal to zero, where zero changes nothing.
        """
        operation = "autocontrast"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def black_and_white(self):
        """
        Uses 'black_and_white' operation on the image.

        Operation converts the image to grayscale.
        """
        self.operation.append("bw")
        return self

    def invert(self):
        """
        Uses 'invert' operation on the image.

        Operation inverts colors of the image.
        """
        self.operation.append("invert")
        return self

    # ART FILTERS
    def duotone(self, value_one=None, value_two=None):
        """
        Uses 'duotone' operation on the image.

        Operation converts an image to use only two colors giving that artistic look. Specifying a value_one
        and value_two is required.

        Args:
            value_one and value_two takes a color value which can be either 6-digit color hex value without
            leading # or the css name of the color.
        """
        operation = "duotone"
        if None not in {value_one, value_two}:
            operation += f":{value_one}:{value_two}"
            self.operation.append(operation)
        else:
            raise ValueError("Duotone required two values")
        return self

    def pixelate(self, strength=None, colors=None, marker=None):
        """
        Uses 'pixelate' operation on the image.

        Operation pixelates the image, reduces the number of colors and enhances some of the edges. Specifying an
        arguments is not required. If there are no values then operation takes default values for all arguments.

        Args:
        strength - the higher, the larger the pixels are. Values between 1-100, the default is 80,
        colors - number of colors. Values between 1-256, the default is 16,
        marker - the higher, the more edges are enhanced by the black marker. Values between 1-100, the default is 40.
        """
        operation = "pixelate"
        if strength is not None:
            operation += f":{strength}"
        if colors is not None:
            operation += f":{colors}"
        if marker is not None:
            operation += f":{marker}"
        self.operation.append(operation)
        return self

    def enhance(self):
        """
        Uses 'enhance' operation on the image.

        Operation adds light to lighter areas and dark to darker areas, intensifies shadows for color that pops.
        """
        self.operation.append("enhance")
        return self

    def mono(self):
        """
        Uses 'mono' operation on the image.

        Operation converts image to grayscale and adds a little bit nostalgic look.
        """
        self.operation.append("mono")
        return self

    def golden(self):
        """
        Uses 'golden' operation on the image.

        Operation adds golden color to the image.
        """
        self.operation.append("golden")
        return self

    # RESIZING
    def resize(self, *args):
        """
        Uses 'resize' operation on the image. Specifying at least one argument is required.

        Operation changes size of the image to given dimensions.

        Args:
            If only one dimension is given with letter h (height) or w (width) at the beginning or at the end,
            the other one will be scaled with respect to aspect ratio.

            If two dimension is given without letters at the beginning or at the end, the image will be resized
            on given values.
        """
        operation = "resize"

        if len(args) == 2:
            width, height = map(int, args)
            operation += f":{width}:{height}"
            self.operation.append(operation)
        elif len(args) == 1:
            value = args[0].strip("wh")
            if args[0].startswith("w") or args[0].endswith("w"):
                operation += f":w{value}"
                self.operation.append(operation)
            elif args[0].startswith("h") or args[0].endswith("h"):
                operation += f":h{value}"
                self.operation.append(operation)
        return self

    def crop(self, *args):
        """
        Uses 'crop' operation on the image.

        Operation crops image for given coordinates. Specifying an arguments is required.

        Args:
            If two coordinates are given then operation crops an image from the top-left corner and given values are:
                arg_one - width,
                arg_two - height.

            If two coordinates are given and the third argument is a string: 'center' then the cropping will center.

            If four coordinates are given then operation crops an image from a selected point and given values are:
                arg_one - width,
                arg_two - height,
                arg_three, arg_four - coordinates of a point from which the crop starts.
        """
        operation = "crop"

        if len(args) == 2:
            value_one, value_two = map(int, args)
            operation += f":{value_one}:{value_two}"
            self.operation.append(operation)
        elif len(args) == 3:
            *tmp, value_three = args
            value_one, value_two, = map(int, tmp)
            if value_three == "center":
                operation += f":{value_one}:{value_two}:{value_three}"
                self.operation.append(operation)
        elif len(args) == 4:
            value_one, value_two, value_three, value_four = map(int, args)
            operation += f":{value_one}:{value_two}:{value_three}:{value_four}"
            self.operation.append(operation)

        return self

    def fit(self, width=None, height=None):
        """
        Uses 'fit' operation on the image.

        Operation resize picture so it fits to given dimensions with respect to aspect ratio.
        Specifying the width and the height is required.

        Args:
            width - dimension of width,
            height - dimension of height.
        """
        operation = "fit"
        if width is not None and height is not None:
            operation += f":{width}:{height}"
            self.operation.append(operation)
        else:
            raise ValueError("fit required two values")
        return self

    def fit_crop(self, width=None, height=None):
        """
        Uses 'fit_crop' operation on the image.

        Operation resize and crop picture so it fits to given dimensions with respect to aspect ratio.
        Images are cropped in a smart way so the most significant object is in the center.

        Args:
            width - dimension of width,
            height - dimension of height.
        """
        operation = "fit_crop"
        if None in {width, height}:
            raise ValueError("fit_crop required two values")
        operation += f":{width}:{height}"
        self.operation.append(operation)
        return self

    # TRANSFORMATION
    def rotate(self, angle=None):
        """
        Uses 'rotate' operation on the image.

        Operation rotates image by any angle. Specifying an argument is not required. If there is no angle value then
        operation takes default value 90.

        Arg:
            angle - int value which can be either negative or positive.
        """
        operation = "rotate"
        if angle is not None:
            operation += f":{angle}"
        self.operation.append(operation)
        return self

    def mirror(self):
        """
        Uses 'mirror' operation on the image.

        Operation mirrors picture.
        """
        self.operation.append("mirror")
        return self

    def flip(self):
        """
        Uses 'flip' operation on the image.

        Operation flips picture vertically.
        """
        self.operation.append("flip")
        return self

    def autorotate(self):
        """
        Uses 'autorotate' operation on the image.

        Operation prevent incorrectly display an image after operations.
        """
        self.operation.append("autorotate")
        return self

    # EDITING
    def bg_color(self, value=None):
        """
        Uses 'bg_color' operation on the image.

        Operation uses bg_color to set background color before other operation which may require it.

        Arg:
            value -  color value which can be either 6-digit color hex value without
            leading # or the css name of the color.
        """
        operation = "bg_color"
        if value is not None:
            operation += f":{value}"
            self.operation.append(operation)
        return self

    # FORMAT
    def format(self, new_extension=None):
        """
        Uses 'format' operation on the image.

        Operation coverts to any of the following formats: jpg, jpeg, webp, png, bmp, tiff, ,tif, jp2.

        Arg:
            new_extension - a string specifying one of the supported formats.
        """
        if new_extension:
            self.extension = f".{new_extension}"
        return self

    # AI OPERATIONS
    def image_labels_list(self):
        """
        Returns a list of possible labels for image determined by AI.

        The function returns a list containing
        the labels (strings) which were recognized by AI.
        """
        json_data = self._json_load_from_url(self.base_url)
        return json_data["extra"]["labels"]

    def image_objects_list(self):
        """
        Returns a list of objects recognized by AI in the image.

        The function returns a list that contains
        the objects on the image (described as strings) if they were
        recognized by AI. Otherwise the function
        returns 'None'.
        """
        json_data = self._json_load_from_url(self.base_url)
        object_list = [label["name"] for label in json_data["extra"]["objects"]]

        return object_list if object_list else None

    def objects_details(self):
        """
        Returns a list of objects with details: {name, bounding box, url}.

        The function returns a list that contains the objects if they were
        recognized by AI. Otherwise function returns 'None'.
        Every each object is defined as a dictionary with details in the following order:

            { 'name': 'object name',
              'bounding_box': [list of vertices coordinates]
              'url': 'url of cropped object'
            }
        """

        json_data = self._json_load_from_url(self.base_url)
        detected = json_data["extra"]["objects"]
        for detected_obj in detected:
            detected_obj.update({"bounding_box": detected_obj["bounding_box"]})

        return detected if detected else None

    def explicit_content(self):
        """
        Returns a boolean type if recognized adult content.

        If the image contains adult content then the function
        returns 'True'. Otherwise returns 'False'.
        """
        json_data = self._json_load_from_url(self.base_url)["extra"]["explicit_content"]

        return any(x in self.EXPLICIT_VALUES for x in json_data.values())

    def is_adult_contents(self):
        """
        Returns a dictionary of adult content categories.

        If artificial intelligence recognized a content for adults
        in the image then function returns a dictionary with pairs
        of the recognized adult category and the possibility of content
        occurrence. For example:
            adult: "LIKELY",
            medical: "VERY_UNLIKELY"
        Otherwise function returns 'None'.
        """
        json_data = self._json_load_from_url(self.base_url)
        adult_result_dict = {}
        explict_content_values = json_data["extra"]["explicit_content"]
        for key, result in explict_content_values.items():
            if result in self.EXPLICIT_VALUES:
                adult_result_dict[key] = result

        return adult_result_dict if adult_result_dict else None

    @property
    def alt_content(self):
        """
        Function returns 'alt' string for image metadata.

        The string for alt is made by concatenation of the image
        labels.
        """

        return " ".join(self.image_labels_list())

    @property
    def url(self):
        if self.operation == []:
            return f"{self.base_url}{','.join(self.operation)}{self.file_name_without_extension}{self.extension}"
        else:
            return f"{self.base_url}{','.join(self.operation)}/{self.file_name_without_extension}{self.extension}"
