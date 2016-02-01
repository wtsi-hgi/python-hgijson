from typing import Any, Iterable, Sequence

from hgijson.json.models import JsonPropertyMapping
from hgijson.models import PropertyMapping
from hgijson.serialization import Serializer, Deserializer
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
        PropertyMapping("d", serialized_property_getter=lambda obj_as_dict: obj_as_dict["serialized_d"],
                        serialized_property_setter=lambda obj_as_dict, value: obj_as_dict.__setitem__(
                            "serialized_d", value),
                        serializer_cls=SimpleModelSerializer, deserializer_cls=SimpleModelDeserializer)
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

    def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
        return PrimitiveSerializer()


class ComplexModelSerializer(SimpleModelSerializer):
    """
    Serializer for `ComplexModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = get_complex_model_property_mappings()
        super().__init__()
        self._property_mappings = custom_mappings

    def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
        if serializer_type == SimpleModelSerializer:
            return SimpleModelSerializer()
        else:
            return super()._create_serializer_of_type(serializer_type)


class SimpleModelDeserializer(Deserializer):
    """
    Deserializer for `SimpleModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = get_simple_model_property_mappings()
        super().__init__(custom_mappings, SimpleModel)

    def _create_deserializer_of_type(self, deserializer_type: type):
        return PrimitiveDeserializer()


class ComplexModelDeserializer(SimpleModelDeserializer):
    """
    Deserializer for `ComplexModel`.
    """
    def __init__(self, custom_mappings: Iterable[PropertyMapping]=None):
        if custom_mappings is None:
            custom_mappings = get_complex_model_property_mappings()
        super().__init__()
        self._property_mappings = custom_mappings
        self._deserializable_cls = ComplexModel

    def _create_deserializer_of_type(self, deserializer_type: type):
        if deserializer_type == SimpleModelDeserializer:
            return SimpleModelDeserializer()
        else:
            return super()._create_deserializer_of_type(deserializer_type)
