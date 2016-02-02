from json import JSONDecoder
from json import JSONEncoder
from typing import Callable, Any, Dict

from hgijson.json._converters import json_decoder_to_deserializer, json_encoder_to_serializer
from hgijson.models import PropertyMapping


class JsonPropertyMapping(PropertyMapping):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self, json_property_name=None, object_property_name: str=None, object_constructor_parameter_name: str=None,
            object_constructor_argument_modifier: Callable[[Any], Any]=None,
            json_property_getter: Callable[[Dict], Any]=None, json_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            encoder_cls: type=JSONEncoder, decoder_cls: type=JSONDecoder):
        """
        Constructor.
        :param json_property_name:
        :param object_property_name:
        :param object_constructor_parameter_name:
        :param object_constructor_argument_modifier:
        :param json_property_getter:
        :param json_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param encoder_cls:
        :param decoder_cls:
        """
        if json_property_name is not None:
            if json_property_getter is not None and json_property_setter is not None:
                raise ValueError("Redundant `json_property_name` argument given. It has been specified that a "
                                 "serialized property is to be used via the given property name and both a setter and "
                                 "getter of this property has been provided. To avoid confusion, the serialized "
                                 "property cannot be specified in this case.")

            if json_property_getter is None:
                def json_property_getter(obj_as_json: dict):
                    return obj_as_json[json_property_name]

            if json_property_setter is None:
                def json_property_setter(obj_as_json: dict, value: Any):
                    obj_as_json[json_property_name] = value

        encoder_as_serializer_cls = json_encoder_to_serializer(encoder_cls)
        decoder_as_serializer_cls = json_decoder_to_deserializer(decoder_cls)

        super().__init__(object_property_name, object_constructor_parameter_name, object_constructor_argument_modifier,
                         json_property_getter, json_property_setter, object_property_getter, object_property_setter,
                         encoder_as_serializer_cls, decoder_as_serializer_cls)

    @property
    def json_property_getter(self) -> Callable[[Dict], Any]:
        return self.serialized_property_getter

    @json_property_getter.setter
    def json_property_getter(self, getter: Callable[[Dict], Any]):
        self.serialized_property_getter = getter

    @property
    def json_property_setter(self) -> Callable[[Any, Any], None]:
        return self.serialized_property_setter

    @json_property_setter.setter
    def json_property_setter(self, setter: Callable[[Any, Any], None]):
        self.serialized_property_setter = setter
