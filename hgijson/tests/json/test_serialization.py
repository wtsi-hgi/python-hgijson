import json
import unittest

from hgijson.tests.json._helpers import create_complex_model_with_json_representation, \
    create_simple_model_with_json_representation
from hgijson.tests.json._serializers import SimpleModelMappingJSONDecoder, ComplexModelMappingJSONDecoder, \
    SimpleModelMappingJSONEncoder, ComplexModelMappingJSONEncoder


class TestMappingJSONEncoder(unittest.TestCase):
    """
    Tests for `MappingJSONEncoder`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]
        self.complex_model = create_complex_model_with_json_representation()[0]
        self.complex_model_as_json = create_complex_model_with_json_representation()[1]

    def test_default_with_unknown(self):
        self.assertRaises(TypeError, SimpleModelMappingJSONEncoder().default, object())

    def test_default_with_simple(self):
        encoded = SimpleModelMappingJSONEncoder().default(self.simple_model)
        self.assertDictEqual(encoded, self.simple_model_as_json)

    def test_default_with_complex(self):
        encoded = ComplexModelMappingJSONEncoder().default(self.complex_model)
        self.assertDictEqual(encoded, self.complex_model_as_json)

    def test_default_with_iterable_with_no_items(self):
        encoded = SimpleModelMappingJSONEncoder().default([])
        self.assertCountEqual(encoded, [])

    def test_default_with_iterable(self):
        simple_models = [create_simple_model_with_json_representation(i)[0] for i in range(10)]
        simple_models_as_json = [create_simple_model_with_json_representation(i)[1] for i in range(10)]
        encoded = SimpleModelMappingJSONEncoder().default(simple_models)
        self.assertCountEqual(encoded, simple_models_as_json)

    def test_class_with_json_dumps(self):
        encoded = json.dumps(self.complex_model, cls=ComplexModelMappingJSONEncoder)
        encoded_as_dict = json.loads(encoded)
        self.assertDictEqual(encoded_as_dict, self.complex_model_as_json)

    def test_class_with_json_dumps_when_iterable(self):
        complex_models = [create_complex_model_with_json_representation(i)[0] for i in range(10)]
        complex_models_as_json = [create_complex_model_with_json_representation(i)[1] for i in range(10)]
        encoded = json.dumps(complex_models, cls=ComplexModelMappingJSONEncoder)
        encoded_as_dict = json.loads(encoded)
        self.assertCountEqual(encoded_as_dict, complex_models_as_json)


class TestMappingJSONDecoder(unittest.TestCase):
    """
    Tests for `MappingJSONDecoder`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]
        self.complex_model = create_complex_model_with_json_representation()[0]
        self.complex_model_as_json = create_complex_model_with_json_representation()[1]

    def test_decode_with_malformed_json(self):
        self.assertRaises(ValueError, SimpleModelMappingJSONDecoder().decode, ":)")

    def test_decode_with_simple(self):
        object_as_json_string = json.dumps(self.simple_model_as_json)
        decoded = SimpleModelMappingJSONDecoder().decode(object_as_json_string)
        self.assertEqual(decoded, self.simple_model)

    def test_decode_with_complex(self):
        object_as_json_string = json.dumps(self.complex_model_as_json)
        decoded = ComplexModelMappingJSONDecoder().decode(object_as_json_string)
        self.assertEqual(decoded, self.complex_model)

    def test_decode_with_iterable_with_no_items(self):
        json_as_string = json.dumps([])
        decoded = SimpleModelMappingJSONDecoder().decode(json_as_string)
        self.assertCountEqual(decoded, [])

    def test_decode_with_iterable(self):
        simple_models = [create_simple_model_with_json_representation(i)[0] for i in range(10)]
        simple_models_as_json = [create_simple_model_with_json_representation(i)[1] for i in range(10)]
        json_as_string = json.dumps(simple_models_as_json)
        decoded = SimpleModelMappingJSONDecoder().decode(json_as_string)
        self.assertCountEqual(decoded, simple_models)

    def test_class_with_json_loads_with_single(self):
        object_as_json_string = json.dumps(self.complex_model_as_json)
        decoded = json.loads(object_as_json_string, cls=ComplexModelMappingJSONDecoder)
        self.assertEqual(decoded, self.complex_model)

    def test_class_with_json_loads_with_iterable(self):
        complex_models = [create_complex_model_with_json_representation(i)[0] for i in range(10)]
        complex_models_as_json = [create_complex_model_with_json_representation(i)[1] for i in range(10)]
        json_as_string = json.dumps(complex_models_as_json)
        decoded = json.loads(json_as_string, cls=ComplexModelMappingJSONDecoder)
        self.assertEqual(decoded, complex_models)


if __name__ == "__main__":
    unittest.main()
