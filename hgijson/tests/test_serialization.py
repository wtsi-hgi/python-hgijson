import json
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


    # def test_deserialize_using_object_property_setter(self):
    #     def object_property_setter_for_b(obj: SimpleModel, value: Any):
    #         obj.b = value + 1
    #
    #     simple_model_b_plus_one = self.simple_model
    #     simple_model_b_plus_one.b += 1
    #     mappings = [JsonPropertyMapping("serialized_a", "a"),
    #                 JsonPropertyMapping("serialized_b", object_property_setter=object_property_setter_for_b)]
    #     deserializer = SimpleModelDeserializer(mappings)
    #     self.assertEqual(deserializer.deserialize(self.simple_model_as_json), simple_model_b_plus_one)
    #
    # def _test_deserialize_instance_to_list_when_collection_support_enabled(self):
    #     # It is not possible to detect this situation - it would depend on the deserializer
    #     pass
    #
    # def test_deserialize_list_when_collection_support_not_enabled(self):
    #     mappings = [JsonPropertyMapping("contains", "my_list", decoder_cls=MyListJSONDecoder, collection_if_list=False)]
    #     ModelWithMyListPropertyJSONDecoder = MappingJSONDecoderClassBuilder(ModelContainingMyList, mappings).build()
    #     decoder = ModelWithMyListPropertyJSONDecoder()  # type: JSONDecoder
    #     to_decode = json.dumps({"contains": [1, 2]})
    #     decoded = decoder.decode(to_decode)
    #     expected = ModelContainingMyList()
    #     expected.my_list = MyList([1, 2])
    #     self.assertEqual(decoded, expected)
    #
    # def _test_deserialize_list_of_list_when_collection_support_not_enabled(self):
    #     # It is not possible to detect this situation - it would depend on the deserializer
    #     pass
    #
    # def test_deserialize_list_of_list_when_collection_support_enabled(self):
    #     mappings = [JsonPropertyMapping("contains", "my_lists", decoder_cls=MyListJSONDecoder, collection_if_list=True)]
    #     ModelWithMyListPropertyJSONDecoder = MappingJSONDecoderClassBuilder(ModelContainingMyList, mappings).build()
    #     decoder = ModelWithMyListPropertyJSONDecoder()  # type: JSONDecoder
    #     my_lists = [[1, i] for i in range(10)]
    #     to_decode = json.dumps({"contains": my_lists})
    #     decoded = decoder.decode(to_decode)
    #     expected = ModelContainingMyList()
    #     expected.my_lists = [MyList(list_item) for list_item in my_lists]
    #     self.assertEqual(decoded, expected)


if __name__ == "__main__":
    unittest.main()
