from typing import Dict, Callable, Any, Set

from hgijson.serializers import PrimitiveDeserializer, PrimitiveSerializer


class PropertyMapping():
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self, object_property_name: str=None, object_constructor_parameter_name: str=None,
            object_constructor_argument_modifier: Callable[[Any], Any]=None,
            serialized_property_getter: Callable[[Dict], Any]=None,
            serialized_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            serializer_cls: type=PrimitiveSerializer, deserializer_cls: type=PrimitiveDeserializer,
            optional: bool=False):
        """
        Constructor.
        :param object_property_name: defines the object property to assign the value returned by
        `serialized_property_getter` to using a simple `object_property_getter` function
        :param object_constructor_parameter_name: defines the constructor parameter to bind the value returned by
        `serialized_property_getter` to using a simple `serialized_property_getter` function
        :param object_constructor_argument_modifier: constructor argument modification function
        :param serialized_property_getter: method that, given the serialized object, gets the property of interest to
        this mapping
        :param serialized_property_setter: method that, given the serialized object, sets a serialized property to the
        value returned by `object_property_getter`
        :param object_property_getter: method that, given the object, gets the property of interest to this mapping
        :param object_property_setter: method that, given the object, sets a property to the value returned by
        `serialized_property_getter`
        :param serializer_cls: class to serialize the value returned by `object_property_getter`
        :param deserializer_cls: class to deserialize the value returned by `serialized_property_getter`
        :param optional: whether the property is optional - will ignore if `None` in serialized representation and will
        not serialize if `None` in object
        """
        if object_property_name is not None:
            # It is not possible to know what the serialized container is therefore default values cannot be set if a
            # required getter/setter is not given. Defaults can however be set in subclasses.

            if object_property_getter is not None and object_property_setter is not None:
                raise ValueError("Redundant `object_property_name` argument given. It has been specified that an "
                                 "object property is to be used via the given property name and both a setter and "
                                 "getter of this property has been provided. To avoid confusion, the object "
                                 "property cannot be specified in this case.")

            if object_property_getter is None:
                def object_property_getter(obj: Any) -> Any:
                    return obj.__getattribute__(object_property_name)

            if object_property_setter is None and object_constructor_parameter_name is None:
                def object_property_setter(obj: Any, value: Any):
                    if not hasattr(obj, object_property_name):
                        raise AttributeError("Object `%s` does not have the attribute `%s`"
                                             % (obj, object_property_name))
                    obj.__setattr__(object_property_name, value)

        if object_constructor_parameter_name is not None:
            if serialized_property_getter is None:
                raise ValueError("`serialized_property_getter` must be defined alongside "
                                 "`object_constructor_parameter_name`.")

            if object_property_setter is not None and object_constructor_parameter_name is not None:
                raise ValueError("`object_property_setter` cannot be defined if `object_constructor_parameter_name` is "
                                 "given as the serialized data will be injected into the object as an argument. If an "
                                 "object property should also be set using a setter, define another mapping. If the "
                                 "constructor argument needs to be modified, use "
                                 "`object_constructor_argument_modifier`.")

            if object_constructor_argument_modifier is None:
                def object_constructor_argument_modifier(argument: Any) -> Any:
                    return argument
        else:
            if object_constructor_argument_modifier is not None:
                raise ValueError("`object_constructor_argument_modifier` cannot be used without "
                                 "`object_constructor_parameter_name` being set.")

        self.serialized_property_getter = serialized_property_getter
        self.serialized_property_setter = serialized_property_setter
        self.object_constructor_parameter_name = object_constructor_parameter_name
        self.object_constructor_argument_modifier = object_constructor_argument_modifier
        self.object_property_getter = object_property_getter
        self.object_property_setter = object_property_setter
        self.serializer_cls = serializer_cls
        self.deserializer_cls = deserializer_cls
        self.optional = optional

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for property_name, value in vars(self).items():
            if other.__dict__[property_name] != self.__dict__[property_name]:
                return False
        return True

    def __str__(self) -> str:
        string_builder = []
        for property, value in vars(self).items():
            if isinstance(value, Set):
                value = str(sorted(value, key=id))
            string_builder.append("%s: %s" % (property, value))
        string_builder = sorted(string_builder)
        return "{ %s }" % ', '.join(string_builder)

    def __repr__(self) -> str:
        return "<%s object at %s: %s>" % (type(self), id(self), str(self))

    def __hash__(self):
        return hash(str(self))
