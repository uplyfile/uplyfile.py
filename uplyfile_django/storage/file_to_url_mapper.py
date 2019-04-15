import json
import logging
from json import JSONDecodeError


class FileToUrlMapper:
    def __init__(self, mappings_filename, initial_mappings=None):
        self._logger = logging.getLogger(__name__)
        self.mappings_filename = mappings_filename
        self.mappings = self._decode_mappings(mappings_filename, initial_mappings)

    def __del__(self):
        self._encode_mappings(self.mappings, self.mappings_filename)

    def save(self, filename, url):
        self.mappings.update({filename: url})

    def get(self, filename):
        url = self.mappings.get(filename)
        if url is None:
            raise KeyError(f"Filename {filename} not mapped to any URL")
        return url

    def is_mapped(self, filename):
        return filename in self.mappings

    def _encode_mappings(self, mappings, filename):
        _mappings = {}
        try:
            with open(filename, "w") as f:
                _mappings = json.dump(mappings, f)
        except (IOError, JSONDecodeError) as e:
            self._logger.critical(f"Error occurred while reading mappings file:\n {e}")
        finally:
            return _mappings

    def _decode_mappings(self, filename, initial_mappings=None):
        mappings = initial_mappings if initial_mappings else {}
        try:
            with open(filename) as f:
                mappings = {**mappings, **json.load(f)}
        except (IOError, JSONDecodeError) as e:
            self._logger.critical(f"Error occurred while reading mappings file:\n {e}")
        finally:
            return mappings
