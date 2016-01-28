import json
from abc import ABCMeta
from json import JSONDecoder, JSONEncoder
from typing import Any, Dict

from hgicommon.serialization.serialization import Deserializer, Serializer
from hgicommon.serialization.serializers import PrimitiveSerializer, PrimitiveDeserializer
from hgicommon.serialization.types import PrimitiveJsonSerializableType, PrimitiveUnionType

_serializer_cache = dict()  # type: Dict[type, Serializer]
_deserializer_cache = dict()    # type: Dict[type, Deserializer]


def json_encoder_to_serializer(encoder_cls: type) -> type:
    """
    Converts a `JSONEncoder` class into an equivalent `Serializer` class.
    :param encoder_cls: the encoder class
    :return: the equivalent `Serializer` class
    """
    if encoder_cls not in _serializer_cache:
        if issubclass(encoder_cls, Serializer):
            encoder_as_serializer_cls = encoder_cls
        else:
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
        if issubclass(decoder_cls, Deserializer):
            encoder_as_deserializer_cls = decoder_cls
        else:
            encoder_as_deserializer_cls = type(
                "%sAsDeserializer" % decoder_cls.__class__.__name__,
                (_JSONDecoderAsDeserializer,),
                {
                    "_DECODER_CLS": decoder_cls
                }
            )
        _deserializer_cache[decoder_cls] = encoder_as_deserializer_cls

    return _deserializer_cache[decoder_cls]


class _JSONEncoderAsSerializer(PrimitiveSerializer, metaclass=ABCMeta):
    """
    JSON encoder wrapped to work as a `Serializer`.

    Subclasses must "override" `_ENCODER_CLS` to specify the `JSONEncoder` to wrap.
    """
    _ENCODER_CLS = type(None)

    def __init__(self, *args, **kwargs):
        if self._ENCODER_CLS == _JSONEncoderAsSerializer._ENCODER_CLS:
            raise RuntimeError(
                    "Subclass of `_JSONEncoderAsSerializer` did not \"override\" `SERIALIZABLE_CLS` constant (it "
                    "cannot be derived from the generic)")

        super().__init__(*args, **kwargs)
        self._encoder = self._ENCODER_CLS(*args, **kwargs)  # type: JSONEncoder

    def serialize(self, serializable: Any) -> PrimitiveUnionType:
        if type(self._encoder) == JSONEncoder:
            # FIXME: There must be a better way of getting the primitive value...
            return json.loads(self._encoder.encode(serializable))
        else:
            return self._encoder.default(serializable)


class _JSONDecoderAsDeserializer(PrimitiveDeserializer, metaclass=ABCMeta):
    """
    JSON decoder wrapped to work as a `Deserializer`.

    Subclasses must "override" `_DECODER_CLS` to specify the `JSONDecoder` to wrap.
    """
    _DECODER_CLS = type(None)

    def __init__(self, *args, **kwargs):
        if self._DECODER_CLS == _JSONDecoderAsDeserializer._DECODER_CLS:
            raise RuntimeError(
                    "Subclass of `_JSONDecoderAsDeserializer` did not \"override\" `SERIALIZABLE_CLS` constant (it "
                    "cannot be derived from the generic)")

        super().__init__(*args, **kwargs)
        self._decoder = self._DECODER_CLS(*args, **kwargs)  # type: JSONDecoder

    def deserialize(self, object_property_value_dict: PrimitiveJsonSerializableType):
        # FIXME: Converting it to a string like this is far from optimal...
        json_as_string = json.dumps(object_property_value_dict)
        return self._decoder.decode(json_as_string)
