import unittest
from typing import Dict

from hgijson.json.models import JsonPropertyMapping
from hgijson.models import PropertyMapping
from hgijson.tests._models import SimpleModel
from hgijson.tests._serializers import ComplexModelSerializer, SimpleModelDeserializer, ComplexModelDeserializer, \
    SimpleModelSerializer
from hgijson.tests.json._helpers import create_complex_model_with_json_representation, \
    create_simple_model_with_json_representation


class TestSerializer(unittest.TestCase):
    """
    Tests for `Serializer`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]
        self.complex_model = create_complex_model_with_json_representation()[0]
        self.complex_model_as_json = create_complex_model_with_json_representation()[1]

    def test_serialize_with_no_mapping(self):
        mappings = [PropertyMapping()]
        serializer = SimpleModelSerializer(mappings)
        self.assertDictEqual(serializer.serialize(self.simple_model), {})

    def test_serialize_using_names(self):
        mappings = [JsonPropertyMapping("serialized_a", "a"), JsonPropertyMapping("serialized_b", "b")]
        serializer = SimpleModelSerializer(mappings)
        self.assertDictEqual(serializer.serialize(self.simple_model), self.simple_model_as_json)

    def test_serialize_using_object_property_getter(self):
        mappings = [JsonPropertyMapping("serialized_b_plus_one", object_property_getter=lambda model: model.b + 1)]
        serializer = SimpleModelSerializer(mappings)
        self.assertDictEqual(serializer.serialize(self.simple_model), {"serialized_b_plus_one": self.simple_model.b + 1})

    def test_serialize_using_serialized_property_setter(self):
        def serialized_property_setter(container: Dict, value: Dict):
            container["augmented_key_%s" % value] = value

        mappings = [JsonPropertyMapping(None, "b", json_property_setter=serialized_property_setter)]
        serializer = ComplexModelSerializer(mappings)
        self.assertDictEqual(serializer.serialize(self.complex_model), {"augmented_key_5": 5})

    def test_serialize_using_serializer_cls(self):
        def serialized_property_setter_for_d(container: Dict, value: Dict):
            container["serialized_d"] = value

        mappings = [PropertyMapping("d", serialized_property_setter=serialized_property_setter_for_d,
                                    serializer_cls=SimpleModelSerializer)]
        serializer = ComplexModelSerializer(mappings)

        complex_model = self.complex_model
        expected = {"serialized_d": [{
            "serialized_a": i,
            "serialized_b": complex_model.b + i
        } for i in range(len(complex_model.d))]}
        self.assertDictEqual(serializer.serialize(complex_model), expected)

    def test_serialize_with_iterable_with_no_items(self):
        serialized = SimpleModelSerializer().serialize([])
        self.assertCountEqual(serialized, [])

    def test_serialize_with_iterable(self):
        complex_models = [create_complex_model_with_json_representation(i)[0] for i in range(10)]
        complex_models_as_json = [create_complex_model_with_json_representation(i)[1] for i in range(10)]
        serialized = ComplexModelSerializer().serialize(complex_models)
        self.assertEqual(serialized, complex_models_as_json)

    def test_serialize_optional_when_not_set(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", optional=True),
                    JsonPropertyMapping("serialized_b", "b", optional=True)]
        serializer = SimpleModelSerializer(mappings)
        self.assertDictEqual(serializer.serialize(SimpleModel()), {})

    def test_serialize_optional_when_set(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", optional=True),
                    JsonPropertyMapping("serialized_b", "b", optional=True)]
        serializer = SimpleModelSerializer(mappings)
        self.assertDictEqual(serializer.serialize(self.simple_model), self.simple_model_as_json)

    def test_serialize_when_property_does_not_exist(self):
        mappings = [JsonPropertyMapping("serialized_a", "z")]
        serializer = SimpleModelSerializer(mappings)
        self.assertRaises(AttributeError, serializer.serialize, self.simple_model)


class TestDeserializer(unittest.TestCase):
    """
    Tests for `Deserializer`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]
        self.complex_model = create_complex_model_with_json_representation()[0]
        self.complex_model_as_json = create_complex_model_with_json_representation()[1]

    def test_deserialize_with_no_mapping(self):
        mappings = [PropertyMapping()]
        deserializer = SimpleModelDeserializer(mappings)
        self.simple_model.a = None
        self.simple_model.b = None
        self.assertEqual(deserializer.deserialize(self.simple_model_as_json), self.simple_model)

    def test_deserialize_using_names(self):
        mappings = [JsonPropertyMapping("serialized_a", "a"), JsonPropertyMapping("serialized_b", "b")]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize(self.simple_model_as_json), self.simple_model)

    def test_deserialize_using_constructor_parameter(self):
        mappings = [JsonPropertyMapping("serialized_a", "a"),
                    JsonPropertyMapping("serialized_b", object_constructor_parameter_name="constructor_b")]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize(self.simple_model_as_json), self.simple_model)

    def test_deserialize_using_constructor_parameter_with_modifier(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", object_constructor_parameter_name="constructor_b",
                                        object_constructor_argument_modifier=lambda value: value + 1)]
        deserializer = SimpleModelDeserializer(mappings)
        model = SimpleModel(self.simple_model_as_json["serialized_a"] + 1)
        self.assertEqual(deserializer.deserialize(self.simple_model_as_json), model)

    def test_deserialize_using_deserializer(self):
        mappings = [JsonPropertyMapping("serialized_a", "a"),
                    JsonPropertyMapping("serialized_b", object_constructor_parameter_name="constructor_b"),
                    JsonPropertyMapping("serialized_c", "c"),
                    PropertyMapping("d", serialized_property_getter=lambda obj_as_dict: obj_as_dict["serialized_d"],
                                    deserializer_cls=SimpleModelDeserializer)]
        deserializer = ComplexModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize(self.complex_model_as_json), self.complex_model)

    def test_deserialize_using_serialized_property_getter(self):
        a_and_b = {
            "ab": [self.simple_model.a, self.simple_model.b]
        }
        mappings = [JsonPropertyMapping(None, "a", json_property_getter=lambda json_as_dict: json_as_dict["ab"][0]),
                    JsonPropertyMapping(None, "b", json_property_getter=lambda json_as_dict: json_as_dict["ab"][1])]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize(a_and_b), self.simple_model)

    def test_deserialize_with_iterable_with_no_items(self):
        decoded = SimpleModelDeserializer().deserialize([])
        self.assertEqual(decoded, [])

    def test_deserialize_with_iterable(self):
        complex_models = [create_complex_model_with_json_representation(i)[0] for i in range(10)]
        complex_models_as_json = [create_complex_model_with_json_representation(i)[1] for i in range(10)]
        decoded = ComplexModelDeserializer().deserialize(complex_models_as_json)
        self.assertEqual(decoded, complex_models)

    def test_deserialize_optional_when_not_set(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", optional=True),
                    JsonPropertyMapping("serialized_b", "b", optional=True)]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize({}), SimpleModel())

    def test_deserialize_optional_when_set(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", optional=True),
                    JsonPropertyMapping("serialized_b", "b", optional=True)]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize(self.simple_model_as_json), self.simple_model)

    def test_deserialize_when_property_does_not_exist(self):
        mappings = [JsonPropertyMapping("serialized_a", "z")]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertRaises(AttributeError, deserializer.deserialize, self.simple_model_as_json)


if __name__ == "__main__":
    unittest.main()
