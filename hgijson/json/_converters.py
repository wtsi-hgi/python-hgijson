import json
from abc import ABCMeta, abstractproperty
from json import JSONDecoder, JSONEncoder
from typing import Any, Dict

from hgijson.json.interfaces import ParsedJSONDecoder
from hgijson.serialization import Deserializer, Serializer
from hgijson.types import PrimitiveJsonSerializableType, PrimitiveUnionType, SerializableType

_serializer_cache = dict()  # type: Dict[type, Serializer]
_deserializer_cache = dict()    # type: Dict[type, Deserializer]

_PLACEHOLDER = object


class _JSONEncoderAsSerializer(Serializer, metaclass=ABCMeta):
    """
    JSON encoder wrapped to work as a `Serializer`.
    """
    @abstractproperty
    def _get_encoder_type(self, *args) -> type:
        """
        Gets the `JSONEncoder` type that is used by this serialiser.
        :return: the encoder type (must be a subclass of `JSONEncoder`)
        """

    def __init__(self, *args, **kwargs):
        super().__init__(())
        json_encoder_cls = self._get_encoder_type()
        self._encoder = json_encoder_cls(*args, **kwargs)  # type: JSONEncoder

    def serialize(self, serializable: SerializableType) -> PrimitiveUnionType:
        if type(self._encoder) == JSONEncoder:
            # Have to load from string to more rich representation - not possible to stop `encode` going to string :/
            return json.loads(self._encoder.encode(serializable))
        else:
            return self._encoder.default(serializable)

    def _create_serializer_of_type(self, serializer_type: type):
        """
        Unused - implemented to satisfy the interface only.
        """

    def _create_serialized_container(self) -> Any:
        """
        Unused - implemented to satisfy the interface only.
        """


class _JSONDecoderAsDeserializer(Deserializer, metaclass=ABCMeta):
    """
    JSON decoder wrapped to work as a `Deserializer`.
    """
    @abstractproperty
    def _get_decoder_type(self, *args) -> type:
        """
        Gets the `JSONDecoder` type that is used by this deserialiser.
        :return: the decoder type (must be a subclass of `JSONDecoder`)
        """

    def __init__(self, *args, **kwargs):
        json_decoder_cls = self._get_decoder_type()
        super().__init__((), json_decoder_cls)
        self._decoder = json_decoder_cls(*args, **kwargs)  # type: JSONDecoder

    def deserialize(self, json_as_dict: PrimitiveJsonSerializableType) -> SerializableType:
        if not isinstance(self._decoder, ParsedJSONDecoder):
            # Decode must take a string (even though we have a richer representation) :/
            json_as_string = json.dumps(json_as_dict)
            return self._decoder.decode(json_as_string)
        else:
            # Optimisation - no need to convert our relatively rich representation into a string (just to turn it back
            # again!)
            return self._decoder.decode_parsed(json_as_dict)

    def _create_deserializer_of_type(self, deserializer_type: type):
        """
        Unused - implemented to satisfy the interface only.
        """


def json_encoder_to_serializer(encoder_cls: type) -> type:
    """
    Converts a `JSONEncoder` class into an equivalent `Serializer` class.
    :param encoder_cls: the encoder class
    :return: the equivalent `Serializer` class
    """
    if encoder_cls not in _serializer_cache:
        encoder_as_serializer_cls = type(
            "%sAsSerializer" % encoder_cls.__class__.__name__,
            (_JSONEncoderAsSerializer,),
            {
                "_get_encoder_type": lambda self: encoder_cls
            }
        )
        _serializer_cache[encoder_cls] = encoder_as_serializer_cls

    return _serializer_cache[encoder_cls]


def json_decoder_to_deserializer(decoder_cls: type) -> type:
    """
    Converts a `JSONDecoder` class into an equivalent `Deserializer` class.
    :param decoder_cls: the decoder class
    :return: the equivalent `Deserializer` class
    """
    if decoder_cls not in _deserializer_cache:
        encoder_as_deserializer_cls = type(
            "%sAsDeserializer" % decoder_cls.__class__.__name__,
            (_JSONDecoderAsDeserializer,),
            {
                "_get_decoder_type": lambda self: decoder_cls
            }
        )
        _deserializer_cache[decoder_cls] = encoder_as_deserializer_cls

    return _deserializer_cache[decoder_cls]
