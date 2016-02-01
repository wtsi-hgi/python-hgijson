import json
import unittest

from hgijson.json._converters import json_encoder_to_serializer, json_decoder_to_deserializer
from hgijson.serialization import Deserializer, Serializer
from hgijson.tests.json._helpers import create_simple_model_with_json_representation
from hgijson.tests.json._serializers import BasicSimpleModelJSONEncoder, BasicSimpleModelJSONDecoder


class TestConverters(unittest.TestCase):
    """
    Tests for `json_encoder_to_serializer` and `json_decoder_to_deserializer`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]

    def test_json_encoder_to_serializer(self):
        serializer_cls = json_encoder_to_serializer(BasicSimpleModelJSONEncoder)
        serializer = serializer_cls()   # type: Serializer
        self.assertIsInstance(serializer, Serializer)

        serialized = serializer.serialize(self.simple_model)
        encoded = BasicSimpleModelJSONEncoder().default(self.simple_model)
        self.assertDictEqual(serialized, encoded)

    def test_json_decoder_to_deserializer(self):
        deserializer_cls = json_decoder_to_deserializer(BasicSimpleModelJSONDecoder)
        deserializer = deserializer_cls()   # type: Deserializer
        self.assertIsInstance(deserializer, Deserializer)

        deserialized = deserializer.deserialize(self.simple_model_as_json)
        decoded = BasicSimpleModelJSONDecoder().decode(json.dumps(self.simple_model_as_json))
        self.assertEqual(deserialized, decoded)


if __name__ == "__main__":
    unittest.main()
