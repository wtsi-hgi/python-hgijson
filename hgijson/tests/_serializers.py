from typing import Any, Iterable, Sequence, List, Type

from hgijson.json_converters.models import JsonPropertyMapping
from hgijson.serialization import Serializer, Deserializer, PropertyMapping
from hgijson.serializers import PrimitiveSerializer, PrimitiveDeserializer
from hgijson.tests._models import SimpleModel, ComplexModel


def get_simple_model_property_mappings() -> Sequence[PropertyMapping]:
    return [
        JsonPropertyMapping("serialized_a", "a"),
        JsonPropertyMapping("serialized_b", "b", "constructor_b")
    ]


def get_complex_model_property_mappings() -> Sequence[PropertyMapping]:
    return [
        JsonPropertyMapping("serialized_b", "b", "constructor_b"),
        JsonPropertyMapping("serialized_c", "c"),
        PropertyMapping(serialized_property_getter=lambda obj_as_dict: obj_as_dict["serialized_d"],
                        serialized_property_setter=lambda obj_as_dict, value: obj_as_dict.__setitem__(
                            "serialized_d", value),
                        object_property_getter=lambda obj: obj.d,
                        object_property_setter=lambda obj, value: setattr(obj, "d", value),
                        serializer_cls=SimpleModelSerializer,
                        deserializer_cls=SimpleModelDeserializer),
        JsonPropertyMapping("serialized_e", "e"),
        JsonPropertyMapping("serialized_f", "f"),
        JsonPropertyMapping("serialized_g", "g"),
        JsonPropertyMapping("serialized_h", "h"),
        JsonPropertyMapping("serialized_i", "i", collection_factory=set, collection_iter=iter),
    ]


class SimpleModelSerializer(Serializer):
    """
    Serializer for `SimpleModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = get_simple_model_property_mappings()
        super().__init__(custom_mappings)

    def _create_serialized_container(self) -> Any:
        return {}

    def _create_serializer_of_type(self, serializer_type: Type) -> Serializer:
        return PrimitiveSerializer()


class ComplexModelSerializer(Serializer):
    """
    Serializer for `ComplexModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = list(get_simple_model_property_mappings()) + list(get_complex_model_property_mappings())
        super().__init__(custom_mappings)

    def _create_serialized_container(self) -> Any:
        return {}

    def _create_serializer_of_type(self, serializer_type: Type) -> Serializer:
        if serializer_type == SimpleModelSerializer:
            return SimpleModelSerializer()
        else:
            return PrimitiveSerializer()


class SimpleModelDeserializer(Deserializer):
    """
    Deserializer for `SimpleModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = get_simple_model_property_mappings()
        super().__init__(custom_mappings, SimpleModel)

    def _create_deserializer_of_type(self, deserializer_type: Type):
        return PrimitiveDeserializer()


class ComplexModelDeserializer(Deserializer):
    """
    Deserializer for `ComplexModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = list(get_simple_model_property_mappings()) + list(get_complex_model_property_mappings())
        super().__init__(custom_mappings, ComplexModel)

    def _create_deserializer_of_type(self, deserializer_type: Type):
        if deserializer_type == SimpleModelDeserializer:
            return SimpleModelDeserializer()
        else:
            return PrimitiveDeserializer()
