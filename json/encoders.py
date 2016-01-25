from abc import ABCMeta
from json import JSONEncoder
from typing import TypeVar, Iterable

from hgicommon.collections import Metadata
from hgicommon.serialization.json.common import JsonPropertyMapping, DefaultSupportedJSONSerializableType


class _MappingJSONEncoder(JSONEncoder, metaclass=ABCMeta):
    """
    JSON encoder that serialises an object based on a mapping of its properties to JSON properties.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    encoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    _PLACEHOLDER = TypeVar("")

    ENCODING_CLS = _PLACEHOLDER     # type: type
    PROPERTY_MAPPINGS = _PLACEHOLDER    # type: Iterable[JsonPropertyMapping]

    def default(self, to_encode: ENCODING_CLS) -> DefaultSupportedJSONSerializableType:
        if self.ENCODING_CLS is _MappingJSONEncoder._PLACEHOLDER:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `ENCODING_CLS` constant")
        if self.PROPERTY_MAPPINGS is _MappingJSONEncoder._PLACEHOLDER:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        if not isinstance(to_encode, self.ENCODING_CLS):
            super().default(to_encode)

        encoded = {}
        for mapping in self.PROPERTY_MAPPINGS:
            assert mapping.json_property not in encoded
            if mapping.object_property is not None:
                encoded[mapping.json_property] = to_encode.__getattribute__(mapping.object_property)

        return encoded


class MetadataJSONEncoder(JSONEncoder):
    """
    JSON encoder for `Metadata` instances.

    Do not use as target_cls in `json.dumps` if the metadata collection being serialised contains values with types that cannot
    be converted to JSON by default. In such cases, this class can be used in `AutomaticJSONEncoderClassBuilder` along
    with encoders that handle other unsupported types or it should be used within another decoder.
    """
    def default(self, to_encode: Metadata) -> DefaultSupportedJSONSerializableType:
        if not isinstance(to_encode, Metadata):
            super().default(to_encode)

        return to_encode._data
