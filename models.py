from typing import Dict, Callable, Any

from hgicommon.models import Model
from hgicommon.serialization.serializers import PrimitiveDeserializer, PrimitiveSerializer


class PropertyMapping(Model):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self,
            serialized_property_name=None, object_property_name: str=None, object_constructor_parameter_name: str=None,
            serialized_property_getter: Callable[[Dict], Any]=None, serialized_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            serializer_cls: type=PrimitiveSerializer, deserializer_cls: type=PrimitiveDeserializer):
        """
        Constructor.
        :param serialized_property_name:
        :param object_property_name:
        :param object_constructor_parameter_name:
        :param serialized_property_getter:
        :param serialized_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param serializer_cls:
        :param deserializer_cls:
        """
        if serialized_property_name is not None:
            if serialized_property_getter is not None and serialized_property_setter is not None:
                raise ValueError("Redundant `serialized_property_name` argument given. It has been specified that a"
                                 "serialized property is to be used via the given property name and both a setter and"
                                 "getter of this property has been provided. To avoid confusion, the serialized "
                                 "property cannot be specified in this case.")

            if serialized_property_getter is None:
                def serialized_property_getter(obj_as_json: dict):
                    return obj_as_json[serialized_property_name]

            if serialized_property_setter is None:
                def serialized_property_setter(obj_as_json: dict, value: Any):
                    obj_as_json[serialized_property_name] = value

        if object_property_name is not None:
            # It is not possible to know what the serialized container is therefore default values cannot be set if a
            # required getter/setter is not given. Defaults can however be set in subclasses.

            if object_property_getter is not None and object_property_setter is not None:
                raise ValueError("Redundant `object_property_name` argument given. It has been specified that an"
                                 "object property is to be used via the given property name and both a setter and"
                                 "getter of this property has been provided. To avoid confusion, the object "
                                 "property cannot be specified in this case.")

            if object_property_getter is None:
                def object_property_getter(obj: Any) -> Any:
                    return obj.__getattribute__(object_property_name)

            if object_property_setter is None:
                def object_property_setter(obj: Any, value: Any):
                    obj.__setattr__(object_property_name, value)

        if object_constructor_parameter_name is not None:
            if serialized_property_getter is None:
                raise ValueError("`serialized_property_getter` or `serialized_property_name` must be defined alongside "
                                 "`object_constructor_parameter_name`")

            if object_property_setter is not None and object_constructor_parameter_name is None:
                raise ValueError("`object_property_setter` cannot be defined if `object_constructor_parameter_name` is "
                                 "given as the serialized data will be injected into the object as an argument. If an "
                                 "object property should also be set using a setter, define another mapping.")

        self.serialized_property_getter = serialized_property_getter
        self.serialized_property_setter = serialized_property_setter
        self.object_property_getter = object_property_getter
        self.object_property_setter = object_property_setter
        self.object_constructor_parameter_name = object_constructor_parameter_name
        self.serializer_cls = serializer_cls
        self.deserializer_cls = deserializer_cls
