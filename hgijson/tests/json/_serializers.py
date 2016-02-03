import json
from json import JSONEncoder, JSONDecoder
from typing import Sequence, Iterable

from hgijson.json._serialization import MappingJSONDecoder, MappingJSONEncoder
from hgijson.json.models import JsonPropertyMapping
from hgijson.types import PrimitiveUnionType
from hgijson.tests._models import SimpleModel, ComplexModel


def get_simple_model_json_property_mappings() -> Sequence[JsonPropertyMapping]:
    return [
        JsonPropertyMapping("serialized_a", "a"),
        JsonPropertyMapping("serialized_b", "b", "constructor_b")
    ]


def get_complex_model_json_property_mappings() -> Sequence[JsonPropertyMapping]:
    return [
        JsonPropertyMapping("serialized_b", "b", "constructor_b"),
        JsonPropertyMapping("serialized_c", "c"),
        JsonPropertyMapping("serialized_d", "d",
                            encoder_cls=SimpleModelMappingJSONEncoder, decoder_cls=SimpleModelMappingJSONDecoder),
        JsonPropertyMapping("serialized_e", "e"),
        JsonPropertyMapping("serialized_f", "f"),
        JsonPropertyMapping("serialized_g", "g"),
        JsonPropertyMapping("serialized_h", "h")
    ]


class BasicSimpleModelJSONEncoder(JSONEncoder):
    """
    Basic JSON encoder for `SimpleModel`.
    """
    def default(self, to_encode: SimpleModel) -> PrimitiveUnionType:
        return {
            "serialized_a": to_encode.a,
            "serialized_b": to_encode.b
        }


class BasicSimpleModelJSONDecoder(JSONDecoder):
    """
    Basic JSON decoder for `SimpleModel`.
    """
    def decode(self, to_decode_as_str: str, *args, **kwargs) -> object:
        to_decode_as_dict = json.loads(to_decode_as_str)

        simple_model = SimpleModel()
        simple_model.a = to_decode_as_dict["serialized_a"]
        simple_model.b = to_decode_as_dict["serialized_b"]
        return simple_model


class SimpleModelMappingJSONEncoder(MappingJSONEncoder):
    """
    Mapping JSON encoder for `SimpleModel`.
    """
    def _get_property_mappings(self) -> Iterable[JsonPropertyMapping]:
        return get_simple_model_json_property_mappings()

    def _get_serializable_cls(self) -> type:
        return SimpleModel


class SimpleModelMappingJSONDecoder(MappingJSONDecoder):
    """
    Mapping JSON decoder for `SimpleModel`.
    """
    def _get_property_mappings(self) -> Iterable[JsonPropertyMapping]:
        return get_simple_model_json_property_mappings()

    def _get_deserializable_cls(self) -> type:
        return SimpleModel


class ComplexModelMappingJSONEncoder(SimpleModelMappingJSONEncoder):
    """
    Mapping JSON encoder for `ComplexModel`.
    """
    def _get_property_mappings(self) -> Iterable[JsonPropertyMapping]:
        # FIXME: Merge correctly, ensure subclass mappings override superclass mappings
        return list(super()._get_property_mappings()) + list(get_complex_model_json_property_mappings())

    def _get_serializable_cls(self) -> type:
        return ComplexModel


class ComplexModelMappingJSONDecoder(SimpleModelMappingJSONDecoder):
    """
    Mapping JSON decoder for `ComplexModel`.
    """
    def _get_property_mappings(self) -> Iterable[JsonPropertyMapping]:
        # FIXME: Merge correctly, ensure subclass mappings override superclass mappings
        return list(super()._get_property_mappings()) + list(get_complex_model_json_property_mappings())

    def _get_deserializable_cls(self) -> type:
        return ComplexModel
