import unittest
from copy import deepcopy

from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from hgijson.tests._models import BaseModel
from hgijson.tests.json_converters._helpers import EXAMPLE_VALUE_1, EXAMPLE_PROPERTY_1, EXAMPLE_PROPERTY_2, \
    EXAMPLE_VALUE_2, EXAMPLE_PROPERTY_3, EXAMPLE_VALUE_3, EXAMPLE_VALUE_4, EXAMPLE_PROPERTY_4


class _Example(BaseModel):
    def __init__(self, example_1=None, example_2=None, example_3=None, *, example_4=None):
        self.example_1 = example_1
        self.example_2 = example_2
        self.example_3 = example_3
        self.example_4 = example_4


_example_mappings = [
    JsonPropertyMapping(EXAMPLE_PROPERTY_1, "example_1", parent_json_properties=["lots", "of", "nesting"]),
    JsonPropertyMapping(EXAMPLE_PROPERTY_2, "example_2", parent_json_properties=["lots", "of", "nesting"]),
    JsonPropertyMapping(json_property_getter=lambda obj_as_json: obj_as_json[EXAMPLE_PROPERTY_3],
                        json_property_setter=lambda obj_as_json, value: obj_as_json.update({EXAMPLE_PROPERTY_3: value}),
                        object_property_name="example_3", parent_json_properties=["more", "nesting"]),
    JsonPropertyMapping(EXAMPLE_PROPERTY_4, "example_4", parent_json_properties=["nesting"], optional=True),
]
_ExampleJSONEncoder = MappingJSONEncoderClassBuilder(_Example, _example_mappings).build()
_ExampleJSONDecoder = MappingJSONDecoderClassBuilder(_Example, _example_mappings).build()


_EXAMPLE = _Example(EXAMPLE_VALUE_1, EXAMPLE_VALUE_2, EXAMPLE_VALUE_3)
_EXAMPLE_AS_JSON = {
    "lots": {
        "of": {
            "nesting": {
                EXAMPLE_PROPERTY_1: EXAMPLE_VALUE_1,
                EXAMPLE_PROPERTY_2: EXAMPLE_VALUE_2
            }
        }
    },
    "more": {
        "nesting": {
            EXAMPLE_PROPERTY_3: EXAMPLE_VALUE_3
        }
    }
}

_EXAMPLE_WITH_OPTIONAL = _Example(EXAMPLE_VALUE_1, EXAMPLE_VALUE_2, EXAMPLE_VALUE_3, example_4=EXAMPLE_VALUE_4)
_EXAMPLE_WITH_OPTIONAL_AS_JSON = dict(**_EXAMPLE_AS_JSON, nesting={EXAMPLE_PROPERTY_4: EXAMPLE_VALUE_4})


class TestParentJsonProperties(unittest.TestCase):
    """
    Tests for ability to user `parent_json_properties`.
    """
    def test_encode(self):
        obj_as_dict = _ExampleJSONEncoder().default(_EXAMPLE)
        self.assertEqual(_EXAMPLE_AS_JSON, obj_as_dict)

    def test_encode_when_optional_is_defined(self):
        obj_as_dict = _ExampleJSONEncoder().default(_EXAMPLE_WITH_OPTIONAL)
        self.assertEqual(_EXAMPLE_WITH_OPTIONAL_AS_JSON, obj_as_dict)

    def test_decode(self):
        obj = _ExampleJSONDecoder().decode_parsed(_EXAMPLE_AS_JSON)
        self.assertEqual(_EXAMPLE, obj)

    def test_decode_when_optional_is_defined(self):
        obj = _ExampleJSONDecoder().decode_parsed(_EXAMPLE_WITH_OPTIONAL_AS_JSON)
        self.assertEqual(_EXAMPLE_WITH_OPTIONAL, obj)

    def test_decode_when_missing_nesting(self):
        example_as_json = deepcopy(_EXAMPLE_AS_JSON)
        del example_as_json["more"]["nesting"]
        self.assertRaises(KeyError, _ExampleJSONDecoder().decode_parsed, example_as_json)


if __name__ == "__main__":
    unittest.main()
