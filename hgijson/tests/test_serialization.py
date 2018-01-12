import unittest
from typing import Iterable, Any, Tuple, Callable, Optional, Dict

from hgijson import JsonPropertyMapping
from hgijson.serialization import PropertyMapping, Serializer, Deserializer
from hgijson.tests._models import SimpleModel, ComplexModel
from hgijson.tests._serializers import SimpleModelDeserializer, SimpleModelSerializer, ComplexModelSerializer, \
    ComplexModelDeserializer
from hgijson.tests.json_converters._helpers import create_complex_model_with_json_representation, \
    create_simple_model_with_json_representation
from hgijson.custom_types import PrimitiveJsonType


class _TestSerialization(unittest.TestCase):
    """
    TODO
    """
    def setUp(self):
        self.simple_model, self.simple_model_as_json = create_simple_model_with_json_representation()
        self.complex_model, self.complex_model_as_json = create_complex_model_with_json_representation()

    def test_serialization_with_no_mapping(self):
        mappings = [PropertyMapping()]
        self._assertSerialization(mappings, {}, SimpleModel())

    def test_serialization_using_names(self):
        mappings = [JsonPropertyMapping("serialized_a", "a"), JsonPropertyMapping("serialized_b", "b")]
        self._assertSerialization(mappings, self.simple_model_as_json, self.simple_model)

    def test_serialization_with_iterable_with_no_items(self):
        self._assertSerialization([], [], [])

    def test_serialization_with_iterable(self):
        simple_models = [create_simple_model_with_json_representation(i)[0] for i in range(10)]
        simple_models_as_json = [create_simple_model_with_json_representation(i)[1] for i in range(10)]
        self._assertSerialization(None, simple_models_as_json, simple_models)

    def test_serialization_optional_when_not_set(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", optional=True),
                    JsonPropertyMapping("serialized_b", "b", optional=True)]
        self._assertSerialization(mappings, {}, SimpleModel())

    def test_serialization_optional_when_set(self):
        mappings = [JsonPropertyMapping("serialized_a", "a", optional=True),
                    JsonPropertyMapping("serialized_b", "b", optional=True)]
        self._assertSerialization(mappings, self.simple_model_as_json, self.simple_model)

    def test_serialization_none(self):
        self._assertSerialization(None, None, None)

    def test_serialization_when_property_does_not_exist(self):
        mappings = [JsonPropertyMapping("serialized_a", "z")]
        self.assertRaises(
            AttributeError, self._assertSerialization, mappings, self.simple_model_as_json, self.simple_model)

    def test_serialization_using_serialization_cls(self):
        mappings = [
            JsonPropertyMapping("serialized_a", "a"),
            JsonPropertyMapping("serialized_b", "b", "constructor_b"),
            JsonPropertyMapping("serialized_c", "c"),
            PropertyMapping(serialized_property_setter=lambda obj, value: obj.__setitem__("serialized_d", value),
                            object_property_getter=lambda obj: obj.d, serializer_cls=SimpleModelSerializer)]
        expected = {
            "serialized_a": self.complex_model.a,
            "serialized_b": self.complex_model.b,
            "serialized_c": self.complex_model.c,
            "serialized_d": [{
                "serialized_a": i,
                "serialized_b": self.complex_model.b + i
            } for i in range(len(self.complex_model.d))]}

        self._assertSerialization(
            mappings, expected, self.complex_model, ComplexModelSerializer, ComplexModelDeserializer)

    def test_serialization_collection(self):
        mappings = [JsonPropertyMapping("serialized_b", "b", "constructor_b"),
                    JsonPropertyMapping("serialized_i", "i", collection_factory=set)]
        expected_serialized = {"serialized_b": self.complex_model_as_json["serialized_b"],
                               "serialized_i": list(self.complex_model.i)}
        expected_deserialized = ComplexModel(self.complex_model.b)
        expected_deserialized.i = self.complex_model.i

        self._assertSerialization(
            mappings, expected_serialized, expected_deserialized, ComplexModelSerializer, ComplexModelDeserializer)

    def _assertSerialization(
            self, mappings: Optional[Iterable[PropertyMapping]], expected_serialized: PrimitiveJsonType,
            expected_deserialized: Any,
            serializer_factory: Callable[[Iterable[PropertyMapping]], Serializer]=SimpleModelSerializer,
            deserializer_factory: Callable[[Iterable[PropertyMapping]], Deserializer]=SimpleModelDeserializer) \
            -> Tuple[PrimitiveJsonType, Any]:
        # TODO: Switch (serialization/deserialization first) order depending on SUT

        serializer = serializer_factory(mappings)
        serialised = serializer.serialize(expected_deserialized)
        self.assertEqual(expected_serialized, serialised)

        deserializer = deserializer_factory(mappings)
        deserialised = deserializer.deserialize(serialised)
        self.assertEqual(expected_deserialized, deserialised)

        return serialised, deserialised


class TestSerializer(_TestSerialization):
    """
    Tests for `Serializer`.
    """
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


class TestDeserializer(_TestSerialization):
    """
    Tests for `Deserializer`.
    """
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

    def test_deserialize_using_serialized_property_getter(self):
        a_and_b = {
            "ab": [self.simple_model.a, self.simple_model.b]
        }
        mappings = [JsonPropertyMapping(None, "a", json_property_getter=lambda json_as_dict: json_as_dict["ab"][0]),
                    JsonPropertyMapping(None, "b", json_property_getter=lambda json_as_dict: json_as_dict["ab"][1])]
        deserializer = SimpleModelDeserializer(mappings)
        self.assertEqual(deserializer.deserialize(a_and_b), self.simple_model)


if __name__ == "__main__":
    unittest.main()
