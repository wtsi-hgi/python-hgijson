from json import JSONEncoder
from typing import Dict, Callable, Any

from hgicommon.serialization.common import PropertyMapping
from hgicommon.serialization.serialization import PrimitiveDeserializer, PrimitiveSerializer, Serializer



class JsonPropertyMapping(PropertyMapping):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self,
            json_property_name=None, object_property_name: str=None, constructor_parameter_name: str=None,
            json_property_getter: Callable[[Dict], Any]=None, json_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            serializer: type=PrimitiveSerializer, deserializer: type=PrimitiveDeserializer):
        """
        TODO
        :param json_property_name:
        :param object_property_name:
        :param constructor_parameter_name:
        :param json_property_getter:
        :param json_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param serializer:
        :param deserializer:
        :return:
        """
        # TODO: Change serializer to encoder, wrapping the encoder into a serializer if required. Same with deserializer
        super().__init__(json_property_name, object_property_name, constructor_parameter_name, json_property_getter,
                         json_property_setter, object_property_getter, object_property_setter, serializer, deserializer)
