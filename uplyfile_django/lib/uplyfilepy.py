import os
import re
import requests
from urllib.parse import urlparse


class UplyImage:
    """
    The UplyImage class gives the ability to create Uplyfile URLs.

    All operations are possible to use as the chainable with the exception
    of AI Operations that are described below.
    """

    EXPLICIT_VALUES = ("VERY_LIKELY", "LIKELY", "POSSIBLE")

    def __init__(self, path):
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
        operation = "avatar"
        if size is not None:
            operation += f":{size}"
        self.operation.append(operation)
        return self

    def face_mark(self):
        self.operation.append("face_mark")
        return self

    def face_crop(self, face_index=None, align=False):
        operation = "face_crop"
        if face_index is not None:
            operation += f":{face_index}"
        if align:
            operation += ":align"
        self.operation.append(operation)
        return self

    # FILE OPTIONS
    def autoformat(self):
        self.operation.append("autoformat")
        return self

    def download(self):
        self.operation.append("download")
        return self

    def quality(self, value):
        operation = "quality"
        if value is not None:
            operation += f":{value}"
        else:
            raise ValueError("Quality requires a value")
        self.operation.append(operation)
        return self

    def progressive(self):
        self.operation.append("progressive")
        return self

    # FILTERS
    def blur(self, strength=None):
        operation = "blur"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def median(self, strength=None):
        operation = "median"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def bilateral(self, strength=None):
        operation = "bilateral"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def sharpen(self, strength=None):
        operation = "sharpen"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def autocontrast(self, strength=None):
        operation = "autocontrast"
        if strength is not None:
            operation += f":{strength}"
        self.operation.append(operation)
        return self

    def black_and_white(self):
        self.operation.append("bw")
        return self

    def invert(self):
        self.operation.append("invert")
        return self

    # ART FILTERS
    def duotone(self, value_one=None, value_two=None):
        operation = "duotone"
        if None not in {value_one, value_two}:
            operation += f":{value_one}:{value_two}"
            self.operation.append(operation)
        else:
            raise ValueError("Duotone required two values")
        return self

    def pixelate(self, strength=None, colors=None, marker=None):
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
        self.operation.append("enhance")
        return self

    def mono(self):
        self.operation.append("mono")
        return self

    def golden(self):
        self.operation.append("golden")
        return self

    # RESIZING
    def resize(self, *args):
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
        operation = "fit"
        if width is not None and height is not None:
            operation += f":{width}:{height}"
            self.operation.append(operation)
        else:
            raise ValueError("fit required two values")
        return self

    def fit_crop(self, width=None, height=None):
        operation = "fit_crop"
        if None in {width, height}:
            raise ValueError("fit_crop required two values")
        operation += f":{width}:{height}"
        self.operation.append(operation)
        return self

    # TRANSFORMATION
    def rotate(self, angle=None):
        operation = "rotate"
        if angle is not None:
            operation += f":{angle}"
        self.operation.append(operation)
        return self

    def mirror(self):
        self.operation.append("mirror")
        return self

    def flip(self):
        self.operation.append("flip")
        return self

    def autorotate(self):
        self.operation.append("autorotate")
        return self

    # EDITING
    def bg_color(self, value=None):
        operation = "bg_color"
        if value is not None:
            operation += f":{value}"
            self.operation.append(operation)
        return self

    # FORMAT
    def format(self, new_extension=None):
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
