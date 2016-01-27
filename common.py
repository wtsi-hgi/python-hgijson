from typing import Tuple, Dict, List, Callable, Any, TypeVar

from hgicommon.models import Model

from hgicommon.serialization.serialization import PrimitiveDeserializer
from hgicommon.serialization.serialization import PrimitiveSerializer


class PropertyMapping(Model):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self,
            serialized_property_name=None, object_property_name: str=None, constructor_parameter_name: str=None,
            serialized_property_getter: Callable[[Dict], Any]=None, serialized_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            serializer_cls: type=PrimitiveSerializer, deserializer_cls: type=PrimitiveDeserializer):
        """
        TODO
        :param serialized_property_name:
        :param object_property_name:
        :param constructor_parameter_name:
        :param serialized_property_getter:
        :param serialized_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param serializer_cls:
        :param deserializer_cls:
        """
        # TODO: Check for too many arguments set

        if serialized_property_name is not None:
            def serialized_property_getter(obj_as_json: dict):
                return obj_as_json[serialized_property_name]

            def serialized_property_setter(obj_as_json: dict, value: Any):
                obj_as_json[serialized_property_name] = value

        if object_property_name is not None:
            def object_property_getter(obj: Any) -> Any:
                return obj.__getattribute__(object_property_name)

            def object_property_setter(obj: Any, value: Any):
                obj.__setattr__(object_property_name, value)

        if constructor_parameter_name is not None and serialized_property_getter is None:
            raise ValueError("Serialized property getter must be defined if constructor parameter is defined")

        self.serialized_property_getter = serialized_property_getter
        self.serialized_property_setter = serialized_property_setter
        self.object_property_getter = object_property_getter
        self.object_property_setter = object_property_setter
        self.constructor_parameter_name = constructor_parameter_name
        self.serializer_cls = serializer_cls
        self.deserializer_cls = deserializer_cls
