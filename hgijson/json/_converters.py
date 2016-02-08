import json
from abc import ABCMeta
from json import JSONDecoder, JSONEncoder
from typing import Any, Dict

from hgijson.json.interfaces import DictJSONDecoder
from hgijson.serialization import Deserializer, Serializer
from hgijson.types import PrimitiveJsonSerializableType, PrimitiveUnionType, SerializableType

_serializer_cache = dict()  # type: Dict[type, Serializer]
_deserializer_cache = dict()    # type: Dict[type, Deserializer]


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
                "_ENCODER_CLS": encoder_cls
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
                "_DECODER_CLS": decoder_cls
            }
        )
        _deserializer_cache[decoder_cls] = encoder_as_deserializer_cls

    return _deserializer_cache[decoder_cls]


class _JSONEncoderAsSerializer(Serializer, metaclass=ABCMeta):
    """
    JSON encoder wrapped to work as a `Serializer`.

    Subclasses must "override" `_ENCODER_CLS` to specify the `JSONEncoder` to wrap.
    """
    _ENCODER_CLS = object()

    def __init__(self, *args, **kwargs):
        assert self._ENCODER_CLS != _JSONEncoderAsSerializer._ENCODER_CLS
        super().__init__(())
        self._encoder = self._ENCODER_CLS(*args, **kwargs)  # type: JSONEncoder

    def serialize(self, serializable: SerializableType) -> PrimitiveUnionType:
        if type(self._encoder) == JSONEncoder:
            # Have to load from string to more rich representation - not possible to stop `encode` going to string :/
            return json.loads(self._encoder.encode(serializable))
        else:
            return self._encoder.default(serializable)

    def _create_serializer_of_type(self, serializer_type: type):
        assert False

    def _create_serialized_container(self) -> Any:
        assert False


class _JSONDecoderAsDeserializer(Deserializer, metaclass=ABCMeta):
    """
    JSON decoder wrapped to work as a `Deserializer`.

    Subclasses must "override" `_DECODER_CLS` to specify the `JSONDecoder` to wrap.
    """
    _DECODER_CLS = object()

    def __init__(self, *args, **kwargs):
        assert self._DECODER_CLS != _JSONDecoderAsDeserializer._DECODER_CLS
        super().__init__((), self._DECODER_CLS)
        self._decoder = self._DECODER_CLS(*args, **kwargs)  # type: JSONDecoder

    def deserialize(self, json_as_dict: PrimitiveJsonSerializableType) -> SerializableType:
        if not isinstance(self._decoder, DictJSONDecoder):
            # Decode must take a string (even though we have a richer representation) :/
            json_as_string = json.dumps(json_as_dict)
            return self._decoder.decode(json_as_string)
        else:
            # Optimisation - no need to convert our relatively rich representation into a string (just to turn it back
            # again!)
            return self._decoder.decode_dict(json_as_dict)

    def _create_deserializer_of_type(self, deserializer_type: type):
        assert False
