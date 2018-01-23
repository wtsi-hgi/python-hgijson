import unittest
from copy import copy
from typing import Iterable

from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder


class _NoPropertyAccess:
    def __init__(self, configurations: Iterable):
        self._configurations = configurations

    def get_configurations(self) -> Iterable:
        return copy(self._configurations)


_no_property_access_mappings = [
    JsonPropertyMapping(json_property_name="configurations", object_constructor_parameter_name="configurations",
                        object_property_getter=lambda obj: obj.get_configurations())
]
_NoPropertyAccessJSONEncoder = MappingJSONEncoderClassBuilder(_NoPropertyAccess, _no_property_access_mappings).build()
_NoPropertyAccessJSONDecoder = MappingJSONDecoderClassBuilder(_NoPropertyAccess, _no_property_access_mappings).build()


class TestNoPropertyAccess(unittest.TestCase):
    """
    Test no object property access support.
    """
    def test_no_property_access(self):
        configurations = [1, 2, 3]
        obj = _NoPropertyAccess(configurations)
        json_as_dict = _NoPropertyAccessJSONEncoder().default(obj)
        self.assertEqual({"configurations": configurations}, json_as_dict)


if __name__ == "__main__":
    unittest.main()
