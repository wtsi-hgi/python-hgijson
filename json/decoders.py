from abc import ABCMeta
from json import JSONDecoder
from typing import Iterable

from hgicommon.serialization.json.common import JsonPropertyMapping

from hgicommon.serialization.serialization import Deserializer, SerializableType


class _MappingJSONDecoder(Deserializer, JSONDecoder, metaclass=ABCMeta):
    """
    JSON decoder that creates an object from JSON based on a mapping from the JSON properties to the object properties,
    mindful that some properties may have to be passed through the constructor.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    decoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    _DESERIALIZABLE_CLS = type(None)     # type: type
    _PROPERTY_MAPPINGS = None    # type: Iterable[JsonPropertyMapping]

    def __init__(self, *args, **kwargs):
        if self._DESERIALIZABLE_CLS is None:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `DECODING_CLS` constant")
        if self._PROPERTY_MAPPINGS is None:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        super().__init__(self._DESERIALIZABLE_CLS, self._PROPERTY_MAPPINGS, *args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    def decode(self, json_as_string: str, **kwargs) -> SerializableType:
        object_as_dict = super().decode(json_as_string)
        return self._decode_json_as_dict(object_as_dict)

    def _decode_json_as_dict(self, object_as_dict: dict) -> SerializableType:
        return self.deserialize(object_as_dict)

    def _create_deserializer_of_type(self, deserializer_type: type) -> Deserializer:
        return deserializer_type(*self._args, **self._kwargs)


class _CollectionMappingJSONDecoder(_MappingJSONDecoder):
    """
    JSON decoder that creates an iterable of objects from JSON based on a mapping from the JSON properties to the object
    properties.
    """
    def _decode_json_as_dict(self, object_as_dict: dict) -> SerializableType:
        deserialized = []
        for deserializable in object_as_dict:
            deserialized.append(self.deserialize(deserializable))
        return deserialized
