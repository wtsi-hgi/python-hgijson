import json
from abc import ABCMeta
from json import JSONDecoder
from typing import Dict, Iterable, TypeVar, Any

from hgicommon.serialization.json.common import DefaultSupportedJSONSerializableType, JsonPropertyMapping


class _MappingJSONDecoder(JSONDecoder, metaclass=ABCMeta):
    """
    JSON decoder that creates an object from JSON based on a mapping from the JSON properties to the object properties,
    mindful that some properties may have to be passed through the constructor.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    decoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    _PLACEHOLDER = TypeVar("")
    DECODING_CLS = _PLACEHOLDER     # type: type
    PROPERTY_MAPPINGS = _PLACEHOLDER    # type: Iterable[JsonPropertyMapping]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._decoders_cache = dict()    # type: Dict[type, JSONDecoder]

    def decode(self, json_as_string: str, **kwargs) -> Any:
        if self.DECODING_CLS is _MappingJSONDecoder._PLACEHOLDER:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `DECODING_CLS` constant")
        if self.PROPERTY_MAPPINGS is _MappingJSONDecoder._PLACEHOLDER:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        json_as_dict = super().decode(json_as_string)

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
        TODO
        :param value:
        :param decoder_type:
        :return:
        """
        if decoder_type == JSONDecoder:
            # Already "primitive" encoding
            return value

        if decoder_type not in self._decoders_cache:
            self._decoders_cache[decoder_type] = decoder_type(*self._args, **self._kwargs)

        value_decoder = self._decoders_cache[decoder_type]
        return value_decoder.decode(json.dumps(value))

