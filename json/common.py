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
            json_property: str, object_property: str=None,
            property_getter: Callable[[Any], Any]=None, property_setter: Callable[[Any, Any], Any]=None,
            constructor_parameter: str=None, encoder: type=JSONEncoder, decoder: type=JSONDecoder):
        """
        TODO
        :param json_property:
        :param object_property:
        :param property_getter:
        :param property_setter:
        :param constructor_parameter:
        :param encoder:
        :param decoder:
        """
        if property_setter is None:
            def property_setter(obj: Any, value: Any):
                obj.__setattr__(object_property, value)

        if property_getter is None:
            def property_getter(obj: Any) -> Any:
                return obj.__getattribute__(object_property)

        self.json_property = json_property
        self.property_getter = property_getter
        self.property_setter = property_setter
        self.constructor_parameter = constructor_parameter
        self.encoder = encoder
        self.decoder = decoder
