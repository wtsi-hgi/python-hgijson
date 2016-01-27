from abc import ABCMeta
from json import JSONEncoder
from typing import Dict
from typing import Iterable

from hgicommon.serialization.json.common import JsonPropertyMapping

from hgicommon.collections import Metadata
from hgicommon.serialization.json.temp import PrimitiveJsonSerializableType
from hgicommon.serialization.serialization import Serializer, SerializableType


class _MappingJSONEncoder(Serializer, JSONEncoder, metaclass=ABCMeta):
    """
    JSON encoder that serialises an object based on a mapping of its properties to JSON properties.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    encoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    SERIALIZABLE_CLS = type(None)     # type: type
    PROPERTY_MAPPINGS = None    # type: Iterable[JsonPropertyMapping]

    def __init__(self, *args, **kwargs):
        if self.SERIALIZABLE_CLS is _MappingJSONEncoder.SERIALIZABLE_CLS:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `SERIALIZABLE_CLS` constant "
                               "(it cannot be derived from the generic)")
        if self.PROPERTY_MAPPINGS is _MappingJSONEncoder.PROPERTY_MAPPINGS:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        super().__init__(self.PROPERTY_MAPPINGS, *args, **kwargs)
        self._args = args
        self._kwargs = kwargs

    def default(self, serializable: SerializableType) -> PrimitiveJsonSerializableType:
        if not isinstance(serializable, self.SERIALIZABLE_CLS):
            JSONEncoder.default(self, serializable)

        return self.serialize(serializable)

    def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
        return serializer_type(*self._args, **self._kwargs)

    def _create_serialized_container(self) -> Dict:
        return {}


class _CollectionMappingJSONEncoder(_MappingJSONEncoder):
    """
    JSON encoder that serialises an iterable of objects based on a mapping of its properties to JSON properties.
    """
    def default(self, serializables: Iterable[SerializableType]) -> PrimitiveJsonSerializableType:
        serialized = []
        for serializable in serializables:
            serialized.append(self.serialize(serializable))
        return serialized


class MetadataJSONEncoder(JSONEncoder):
    """
    JSON encoder for `Metadata` instances.

    Do not use as target_cls in `json.dumps` if the metadata collection being serialised contains values with types that cannot
    be converted to JSON by default. In such cases, this class can be used in `AutomaticJSONEncoderClassBuilder` along
    with encoders that handle other unsupported types or it should be used within another decoder.
    """
    def default(self, to_encode: Metadata) -> PrimitiveJsonSerializableType:
        if not isinstance(to_encode, Metadata):
            JSONEncoder.default(self, to_encode)

        return to_encode._data
