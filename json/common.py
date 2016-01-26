from json import JSONDecoder, JSONEncoder
from typing import Tuple, Dict, Union, List, Callable, Any

from hgicommon.models import Model


DefaultSupportedJSONSerializableType = Union[
    Dict, List, Tuple, str, int, float, bool, None
]


class JsonPropertyMapping(Model):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self,
            json_property: str=None, object_property: str=None, constructor_parameter: str=None,
            json_property_getter: Callable[[Dict], Any]=None, json_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            encoder: type=JSONEncoder, decoder: type=JSONDecoder):
        """
        TODO
        :param json_property:
        :param object_property:
        :param constructor_parameter:
        :param json_property_getter:
        :param json_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param encoder:
        :param decoder:
        :return:
        """
        if json_property is None:
            if json_property_getter is None:
                raise ValueError("No way to get the JSON property")
            if json_property_setter is None:
                raise ValueError("No way to map the JSON property")
        if object_property is None:
            if object_property_getter is None:
                raise ValueError("No way to get the object property")
            if constructor_parameter is None and object_property_setter is None:
                raise ValueError("No way to set the object property")

        if json_property_getter is None:
            def json_property_getter(obj_as_json: dict):
                return obj_as_json[json_property]

        if json_property_setter is None:
            def json_property_setter(obj_as_json: dict, value: Any):
                obj_as_json[json_property] = value

        if object_property_getter is None:
            def object_property_getter(obj: Any) -> Any:
                return obj.__getattribute__(object_property)

        if object_property_setter is None:
            if constructor_parameter is None:
                def object_property_setter(obj: Any, value: Any):
                    obj.__setattr__(object_property, value)

        assert json_property_getter is not None
        assert json_property_setter is not None
        assert object_property_getter is not None
        assert object_property_setter is not None or constructor_parameter is not None

        self.json_property_getter = json_property_getter
        self.json_property_setter = json_property_setter
        self.object_property_getter = object_property_getter
        self.object_property_setter = object_property_setter
        self.constructor_parameter = constructor_parameter
        self.encoder = encoder
        self.decoder = decoder
