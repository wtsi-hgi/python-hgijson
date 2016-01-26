import json
from abc import ABCMeta
from json import JSONDecoder
from typing import Dict, Iterable, TypeVar, Any

from hgicommon.serialization.json.common import DefaultSupportedJSONSerializableType, JsonPropertyMapping
from hgicommon.serialization.json.encoders import _MappingJSONEncoder


class _MappingJSONDecoder(JSONDecoder, metaclass=ABCMeta):
    """
    JSON decoder that creates an object from JSON based on a mapping from the JSON properties to the object properties,
    mindful that some properties may have to be passed through the constructor.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    decoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    DECODING_CLS = type(None)     # type: type
    PROPERTY_MAPPINGS = None    # type: Iterable[JsonPropertyMapping]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._decoders_cache = dict()    # type: Dict[type, JSONDecoder]

    def decode(self, json_as_string: str, **kwargs) -> Any:
        if self.DECODING_CLS is None:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `DECODING_CLS` constant")
        if self.PROPERTY_MAPPINGS is None:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        json_as_dict = super().decode(json_as_string)
        return self._decode_json_as_dict(json_as_dict)

    def _decode_json_as_dict(self, json_as_dict: dict) -> Any:
        """
        TODO
        :param json_as_dict:
        :return:
        """
        init_kwargs = dict()    # Dict[str, Any]
        for mapping in self.PROPERTY_MAPPINGS:
            if mapping.constructor_parameter is not None:
                value = json_as_dict[mapping.json_property]
                init_kwargs[mapping.constructor_parameter] = self._decode_property_value(value, mapping.decoder)

        decoded = self.DECODING_CLS(**init_kwargs)

        for mapping in self.PROPERTY_MAPPINGS:
            if mapping.constructor_parameter is None:
                value = json_as_dict[mapping.json_property]
                decoded.__setattr__(mapping.object_property, self._decode_property_value(value, mapping.decoder))

        return decoded

    def _decode_property_value(self, value: DefaultSupportedJSONSerializableType, decoder_type: type) -> Any:
        """
        Dencode the given value using an decoder of the given type.
        :param value: the value to decode
        :param decoder_type: the type of decoder to decode the value with
        :return: decoded value
        """
        if decoder_type == JSONDecoder:
            # Already "primitive" encoding
            return value

        if decoder_type not in self._decoders_cache:
            self._decoders_cache[decoder_type] = decoder_type(*self._args, **self._kwargs)

        value_decoder = self._decoders_cache[decoder_type]
        return value_decoder.decode(json.dumps(value))


class _CollectionMappingJSONDecoder(_MappingJSONDecoder):
    """
    JSON decoder that creates an iterable of objects from JSON based on a mapping from the JSON properties to the object
    properties.
    """
    def _decode_json_as_dict(self, json_as_dict: dict) -> Any:
        decoded = []
        for x in json_as_dict:
            decoded.append(super()._decode_json_as_dict(x))
        return decoded