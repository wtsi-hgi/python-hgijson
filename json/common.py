import json
from json import JSONEncoder, JSONDecoder
from typing import Dict, Callable, Any

from hgicommon.serialization.common import PropertyMapping
from hgicommon.serialization.json.temp import PrimitiveJsonSerializableType
from hgicommon.serialization.serialization import PrimitiveDeserializer, PrimitiveSerializer, Serializer, Deserializer, \
    PrimitiveUnionType


class JsonPropertyMapping(PropertyMapping):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self,
            json_property_name=None, object_property_name: str=None, constructor_parameter_name: str=None,
            json_property_getter: Callable[[Dict], Any]=None, json_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            encoder_cls: type=JSONEncoder, decoder_cls: type=JSONDecoder):
        """
        TODO
        :param json_property_name:
        :param object_property_name:
        :param constructor_parameter_name:
        :param json_property_getter:
        :param json_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param encoder_cls:
        :param decoder_cls:
        :return:
        """
        encoder_as_serializer_cls = _BuildJSONEncoderAsSerializer(encoder_cls).build()
        decoder_as_serializer_cls = _BuildJSONDecoderAsDeserializer(decoder_cls).build()

        super().__init__(json_property_name, object_property_name, constructor_parameter_name, json_property_getter,
                         json_property_setter, object_property_getter, object_property_setter,
                         encoder_as_serializer_cls, decoder_as_serializer_cls)


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

    def deserialize(self, object_as_json: PrimitiveJsonSerializableType):
        # TODO: Converting it to a string like this is far from optimal...
        json_as_string = json.dumps(object_as_json)
        return self._decoder.decode(json_as_string)


class _BuildJSONEncoderAsSerializer:
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
        if self.encoder_cls not in _BuildJSONEncoderAsSerializer._serializer_cache:
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
            _BuildJSONEncoderAsSerializer._serializer_cache[self.encoder_cls] = encoder_as_serializer_cls

        return _BuildJSONEncoderAsSerializer._serializer_cache[self.encoder_cls]


class _BuildJSONDecoderAsDeserializer:
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
        if self.decoder_cls not in _BuildJSONDecoderAsDeserializer._deserializer_cache:
            if issubclass(self.decoder_cls, Serializer):
                encoder_as_deserializer_cls = self.decoder_cls
            else:
                encoder_as_deserializer_cls = type(
                    "%sAsDeserializer" % self.decoder_cls.__class__.__name__,
                    (_JSONDecoderAsDeserializer,),
                    {
                        "_DECODER_CLS": self.decoder_cls
                    }
                )
            _BuildJSONDecoderAsDeserializer._deserializer_cache[self.decoder_cls] = encoder_as_deserializer_cls

        return _BuildJSONDecoderAsDeserializer._deserializer_cache[self.decoder_cls]
