from abc import ABCMeta
from json import JSONDecoder
from typing import Iterable, TypeVar

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

    def decode(self, json_as_string: str, **kwargs) -> DefaultSupportedJSONSerializableType:
        if self.DECODING_CLS is _MappingJSONDecoder._PLACEHOLDER:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `DECODING_CLS` constant")
        if self.PROPERTY_MAPPINGS is _MappingJSONDecoder._PLACEHOLDER:
            raise RuntimeError("Subclass of `_MappingJSONEncoder` did not \"override\" `PROPERTY_MAPPINGS` constant")

        json_as_dict = super().decode(json_as_string)

        init_kwargs = dict()    # Dict[str, Any]
        for mapping in self.PROPERTY_MAPPINGS:
            if mapping.constructor_argument is not None:
                init_kwargs[mapping.constructor_argument] = json_as_dict[mapping.json_property]

        model = self.DECODING_CLS(**init_kwargs)

        for mapping in self.PROPERTY_MAPPINGS:
            if mapping.constructor_argument is None:
                model.__setattr__(mapping.object_property, json_as_dict[mapping.json_property])

        return model
