import os
import re
from urllib.parse import urlparse


class UplyImage:
    def __init__(self, path):
        self.path = path
        self.base_url, self.file_name = path.rsplit("/", 1)
        self.raise_if_invalid_url(path)
        self.remove_operations_from_url(path)
        self.file_name_without_extension, self.extension = os.path.splitext(
            self.file_name
        )
        self.operation = []

    def raise_if_invalid_url(self, path):
        parse = urlparse(path)
        if not re.match(r"/\w+/\w+/", parse.path):
            raise ValueError("Please enter correct path.")

    def remove_operations_from_url(self, path):
        parse = urlparse(path)
        start, stop = re.match(r"/\w+/\w+/", parse.path).span()
        self.base_url = f"{parse.scheme}://{parse.netloc}" + parse.path[start:stop]

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

    @property
    def url(self):
        if self.operation == []:
            return f"{self.base_url}{','.join(self.operation)}{self.file_name_without_extension}{self.extension}"
        else:
            return f"{self.base_url}{','.join(self.operation)}/{self.file_name_without_extension}{self.extension}"
