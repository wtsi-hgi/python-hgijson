from json import JSONDecoder
from json import JSONEncoder
from typing import Callable, Any, Dict

from hgicommon.serialization.json._converters import json_decoder_to_deserializer, json_encoder_to_serializer
from hgicommon.serialization.models import PropertyMapping


class JsonPropertyMapping(PropertyMapping):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self,
            json_property_name=None, object_property_name: str=None, object_constructor_parameter_name: str=None,
            json_property_getter: Callable[[Dict], Any]=None, json_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            encoder_cls: type=JSONEncoder, decoder_cls: type=JSONDecoder):
        """
        TODO
        :param json_property_name:
        :param object_property_name:
        :param object_constructor_parameter_name:
        :param json_property_getter:
        :param json_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param encoder_cls:
        :param decoder_cls:
        :return:
        """
        encoder_as_serializer_cls = json_encoder_to_serializer(encoder_cls)
        decoder_as_serializer_cls = json_decoder_to_deserializer(decoder_cls)

        # TODO: Set default JSON property getter/setter if name specified

        super().__init__(json_property_name, object_property_name, object_constructor_parameter_name, json_property_getter,
                         json_property_setter, object_property_getter, object_property_setter,
                         encoder_as_serializer_cls, decoder_as_serializer_cls)
