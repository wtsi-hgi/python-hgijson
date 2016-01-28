import json
from json import JSONEncoder, JSONDecoder
from typing import Dict, Callable, Any

from hgicommon.serialization.models import PropertyMapping
from hgicommon.serialization.serialization import Deserializer
from hgicommon.serialization.serialization import Serializer
from hgicommon.serialization.serializers import PrimitiveSerializer, PrimitiveDeserializer
from hgicommon.serialization.types import PrimitiveJsonSerializableType, PrimitiveUnionType



class _JSONEncoderAsSerializer(PrimitiveSerializer):
    """
    TODO
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


class _JSONDecoderAsDeserializer(PrimitiveDeserializer):
    """
    TODO
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
        # TODO: Converting it to a string like this is far from optimal...
        json_as_string = json.dumps(object_property_value_dict)
        return self._decoder.decode(json_as_string)


class BuildJSONEncoderAsSerializer:
    """
    TODO
    """
    _serializer_cache = dict() # type: Dict[type, Serializer]

    def __init__(self, encoder_cls: type):
        """
        TODO
        :param encoder_cls:
        :return:
        """
        self.encoder_cls = encoder_cls

    def build(self) -> type:
        """
        TODO
        :return:
        """
        if self.encoder_cls not in BuildJSONEncoderAsSerializer._serializer_cache:
            if issubclass(self.encoder_cls, Serializer):
                encoder_as_serializer_cls = self.encoder_cls
            else:
                encoder_as_serializer_cls = type(
                    "%sAsSerializer" % self.encoder_cls.__class__.__name__,
                    (_JSONEncoderAsSerializer,),
                    {
                        "_ENCODER_CLS": self.encoder_cls
                    }
                )
            BuildJSONEncoderAsSerializer._serializer_cache[self.encoder_cls] = encoder_as_serializer_cls

        return BuildJSONEncoderAsSerializer._serializer_cache[self.encoder_cls]


class BuildJSONDecoderAsDeserializer:
    """
    TODO
    """
    _deserializer_cache = dict() # type: Dict[type, Deserializer]

    def __init__(self, decoder_cls: type):
        """
        TODO
        :param decoder_cls:
        :return:
        """
        self.decoder_cls = decoder_cls

    def build(self) -> type:
        """
        TODO
        :return:
        """
        if self.decoder_cls not in BuildJSONDecoderAsDeserializer._deserializer_cache:
            if issubclass(self.decoder_cls, Deserializer):
                encoder_as_deserializer_cls = self.decoder_cls
            else:
                encoder_as_deserializer_cls = type(
                    "%sAsDeserializer" % self.decoder_cls.__class__.__name__,
                    (_JSONDecoderAsDeserializer,),
                    {
                        "_DECODER_CLS": self.decoder_cls
                    }
                )
            BuildJSONDecoderAsDeserializer._deserializer_cache[self.decoder_cls] = encoder_as_deserializer_cls

        return BuildJSONDecoderAsDeserializer._deserializer_cache[self.decoder_cls]
