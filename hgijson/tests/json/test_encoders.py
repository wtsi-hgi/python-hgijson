import json
import unittest

from hgicommon.collections import Metadata
from hgijson.json.encoders import MetadataJSONEncoder


class TestMetadataJSONEncoder(unittest.TestCase):
    """
    Tests for `MetadataJSONEncoder`.
    """
    def setUp(self):
        self.metadata_as_json = {
            "a": 10,
            "b": "test",
            "c": [1, 2, 3],
            "e": 1.5
        }
        self.metadata = Metadata(self.metadata_as_json)

    def test_default_with_unknown(self):
        self.assertRaises(TypeError, MetadataJSONEncoder().default, object())

    def test_default_with_metadata(self):
        encoded = MetadataJSONEncoder().default(self.metadata)
        self.assertDictEqual(encoded, self.metadata_as_json)

    def test_class_with_json_dumps(self):
        encoded_as_string = json.dumps(self.metadata, cls=MetadataJSONEncoder)
        encoded = json.loads(encoded_as_string)
        self.assertDictEqual(encoded, self.metadata_as_json)


if __name__ == "__main__":
    unittest.main()
