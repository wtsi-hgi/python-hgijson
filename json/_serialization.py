from abc import ABCMeta
from json import JSONEncoder, JSONDecoder
from typing import Dict, Union
from typing import Iterable

from hgicommon import collections
from hgicommon.serialization.serialization import Serializer, Deserializer
from hgicommon.serialization.types import PrimitiveJsonSerializableType
from hgicommon.serialization.types import SerializableType


class MappingJSONEncoder(Serializer, JSONEncoder, metaclass=ABCMeta):
    """
    JSON encoder that serialises an object based on a mapping of its properties to JSON properties.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    encoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    _SERIALIZABLE_CLS = type(None)     # type: type
    _PROPERTY_MAPPINGS = None    # type_but_do_not_static_check_as_cannot_import: Iterable[JsonPropertyMapping]

    def __init__(self, *args, **kwargs):
        if self._SERIALIZABLE_CLS is MappingJSONEncoder._SERIALIZABLE_CLS:
            raise RuntimeError("Subclass of `MappingJSONEncoder` did not \"override\" `SERIALIZABLE_CLS` constant "
                               "(it cannot be derived from the generic)")
        if self._PROPERTY_MAPPINGS is MappingJSONEncoder._PROPERTY_MAPPINGS:
            raise RuntimeError("Subclass of `MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        super().__init__(self._PROPERTY_MAPPINGS, *args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    def default(self, serializable: Union[SerializableType, Iterable[SerializableType]]) -> PrimitiveJsonSerializableType:
        if not isinstance(serializable, self._SERIALIZABLE_CLS):
            JSONEncoder.default(self, serializable)

        return self.serialize(serializable)

    def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
        return serializer_type(*self._args, **self._kwargs)

    def _create_serialized_container(self) -> Dict:
        return {}


class MappingJSONDecoder(Deserializer, JSONDecoder, metaclass=ABCMeta):
    """
    JSON decoder that creates an object from JSON based on a mapping from the JSON properties to the object properties,
    mindful that some properties may have to be passed through the constructor.

    Can decode collections of the deserializable object.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    decoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    _DESERIALIZABLE_CLS = type(None)     # type: type
    _PROPERTY_MAPPINGS = None    # type_but_do_not_static_check_as_cannot_import: Iterable[JsonPropertyMapping]

    def __init__(self, *args, **kwargs):
        if self._DESERIALIZABLE_CLS is None:
            raise RuntimeError("Subclass of `MappingJSONEncoder` did not \"override\" `DECODING_CLS` constant")
        if self._PROPERTY_MAPPINGS is None:
            raise RuntimeError("Subclass of `MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        super().__init__(self._PROPERTY_MAPPINGS, self._DESERIALIZABLE_CLS, *args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    def decode(self, json_as_string: str, **kwargs) -> SerializableType:
        parsed_json = super().decode(json_as_string)

        if isinstance(parsed_json, list):
            decoded = []
            for instance_as_json in parsed_json:
                decoded.append(self._decode_json_as_dict(instance_as_json))
            return decoded

        return self._decode_json_as_dict(parsed_json)

    def _decode_json_as_dict(self, object_as_dict: dict) -> SerializableType:
        return self.deserialize(object_as_dict)

    def _create_deserializer_of_type(self, deserializer_type: type) -> Deserializer:
        return deserializer_type(*self._args, **self._kwargs)
