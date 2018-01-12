from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Union, Dict, List, Optional, Iterable, Type, Callable

from hgijson.custom_types import SerializableType, PrimitiveUnionType, PrimitiveJsonType


class PropertyMapping:
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self, *,
            serialized_property_getter: Callable[[Dict], Any]=None,
            serialized_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            object_constructor_parameter_name: str = None,
            object_constructor_argument_modifier: Callable[[Any], Any] = None,
            serializer_cls: Type["Serializer"]=None,
            deserializer_cls: Type["Deserializer"]=None,
            optional: bool=False,
            collection_factory: Callable[[Iterable], Any]=lambda items: list(items),
            collection_iter: Callable[[Any], Iterable]=lambda collection: iter(collection)):
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
        :param serializer_cls: class to serialize the value returned by `object_property_getter` (defaults to
        PrimitiveSerializer)
        :param deserializer_cls: class to deserialize the value returned by `serialized_property_getter` (defaults to
        PrimitiveDeserializer)
        :param optional: whether the property is optional - will ignore if `None` in serialized representation and will
        not serialize if `None` in object
        """
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

        from hgijson.serializers import PrimitiveSerializer, PrimitiveDeserializer

        self.serialized_property_getter = serialized_property_getter
        self.serialized_property_setter = serialized_property_setter
        self.object_constructor_parameter_name = object_constructor_parameter_name
        self.object_constructor_argument_modifier = object_constructor_argument_modifier
        self.object_property_getter = object_property_getter
        self.object_property_setter = object_property_setter
        self.serializer_cls = serializer_cls if serializer_cls is not None else PrimitiveSerializer
        self.deserializer_cls = deserializer_cls if deserializer_cls is not None else PrimitiveDeserializer
        self.optional = optional
        self.collection_factory = collection_factory
        self.collection_iter = collection_iter

    def __str__(self) -> str:
        string_builder = []
        for property, value in vars(self).items():
            string_builder.append("%s: %s" % (property, value))
        string_builder = sorted(string_builder)
        return "{ %s }" % ', '.join(string_builder)

    def __repr__(self) -> str:
        return "<%s object at %s: %s>" % (type(self), id(self), str(self))


class Serializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    Serializer that uses a mapping that describes how the process should occur for the type of serializable object that
    this serializer handles.
    """
    @abstractmethod
    def _create_serializer_of_type(self, serializer_type: Type) -> "Serializer":
        """
        Create an instance of an serializer of the given type.
        :param serializer_type: the type of serializer to instantiate (a subclass of `Serializer`)
        :return: the created serializer
        """

    @abstractmethod
    def _create_serialized_container(self) -> Any:
        """
        Create the container in which serialized representation is built in
        :return: the container
        """

    def __init__(self, property_mappings: Iterable[PropertyMapping]):
        """
        Constructor.
        :param property_mappings: the property mappings (of type `List[PropertyMapping]`)
        """
        self._property_mappings = property_mappings     # type: Iterable[PropertyMapping]
        self._serializers_cache = dict()    # type: Dict[type, Serializer]

    def serialize(self, serializable: Optional[Union[SerializableType, List[SerializableType]]]) \
            -> PrimitiveJsonType:
        """
        Serializes the given serializable object or collection of serializable objects.
        :param serializable: the object or objects to serialize
        :return: a serialization of the given object
        """
        if serializable is None:
            # Implements #17
            return None
        elif isinstance(serializable, List):
            return [self.serialize(item) for item in serializable]
        else:
            serialized = self._create_serialized_container()

            for mapping in self._property_mappings:
                if mapping.object_property_getter is not None and mapping.serialized_property_setter is not None:
                    value = mapping.object_property_getter(serializable)
                    if not (mapping.optional and value is None):
                        if isinstance(value, type(mapping.collection_factory([]))):
                            value = list(mapping.collection_iter(value))
                        encoded_value = self._serialize_property_value(value, mapping.serializer_cls)
                        mapping.serialized_property_setter(serialized, encoded_value)

            return serialized

    def _serialize_property_value(self, to_serialize: Any, serializer_cls: Type) -> Any:
        """
        Serializes the given value using the given serializer.
        :param to_serialize: the value to deserialize
        :param serializer_cls: the type of serializer to use
        :return: serialized value
        """
        serializer = self._create_serializer_of_type_with_cache(serializer_cls)
        assert serializer is not None
        return serializer.serialize(to_serialize)

    def _create_serializer_of_type_with_cache(self, serializer_type: Type) -> "Serializer":
        """
        Creates a deserializer of the given type, exploiting a cache.
        :param serializer_type: the type of deserializer to create
        :return: the created serializer
        """
        if serializer_type not in self._serializers_cache:
            self._serializers_cache[serializer_type] = self._create_serializer_of_type(serializer_type)
        return self._serializers_cache[serializer_type]


class Deserializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    Deserializer that uses a mapping that describes how the process should occur for the type of deserializable object
    that this deserializer handles.
    """
    @abstractmethod
    def _create_deserializer_of_type(self, deserializer_type: Type) -> "Deserializer":
        """
        Creates a deserializer of the given type.
        :param deserializer_type: the type of deserializer to create
        :return: the created deserializer
        """

    def __init__(self, property_mappings: Iterable[PropertyMapping], deserializable_cls: Type):
        """
        Constructor.
        :param property_mappings: TODO
        :param deserializable_cls: the class that should be built as a result of deserialization
        """
        self._property_mappings = property_mappings     # type: Iterable[PropertyMapping]
        self._deserializable_cls = deserializable_cls
        self._deserializers_cache = dict()    # type: Dict[type, Deserializer]

    def deserialize(self, to_deserialize: PrimitiveJsonType) \
            -> Optional[Union[SerializableType, List[SerializableType]]]:
        """
        Deserializes the given representation of the serialized object.
        :param to_deserialize: the serialized object as a dictionary
        :return: the deserialized object or collection of deserialized objects
        """
        if to_deserialize is None:
            # Implements #17
            return None
        elif isinstance(to_deserialize, List):
            deserialized = []
            for item in to_deserialize:
                item_deserialized = self.deserialize(item)
                deserialized.append(item_deserialized)
            return deserialized
        else:
            mappings_not_set_in_constructor = []    # type: List[PropertyMapping]

            init_kwargs = dict()    # type: Dict[str, Any]
            for mapping in self._property_mappings:
                if mapping.object_constructor_parameter_name is not None:
                    value = mapping.serialized_property_getter(to_deserialize)
                    if not (mapping.optional and value is None):
                        decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
                        if isinstance(decoded_value, list):
                            collection = mapping.collection_factory(decoded_value)
                            decoded_value = collection

                        argument = mapping.object_constructor_argument_modifier(decoded_value)
                        init_kwargs[mapping.object_constructor_parameter_name] = argument
                else:
                    mappings_not_set_in_constructor.append(mapping)

            decoded = self._deserializable_cls(**init_kwargs)
            assert type(decoded) == self._deserializable_cls

            for mapping in mappings_not_set_in_constructor:
                assert mapping.object_constructor_parameter_name is None
                if mapping.serialized_property_getter is not None and mapping.object_property_setter is not None:
                    value = mapping.serialized_property_getter(to_deserialize)
                    if not (mapping.optional and value is None):
                        decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
                        if isinstance(decoded_value, list):
                            collection = mapping.collection_factory(decoded_value)
                            decoded_value = collection

                        mapping.object_property_setter(decoded, decoded_value)

            return decoded

    def _deserialize_property_value(self, to_deserialize: PrimitiveJsonType, deserializer_cls: Type) -> Any:
        """
        Deserializes the given value using the given deserializer.
        :param to_deserialize: the value to deserialize
        :param deserializer_cls: the type of deserializer to use
        :return: deserialized value
        """
        deserializer = self._create_deserializer_of_type_with_cache(deserializer_cls)
        assert deserializer is not None
        return deserializer.deserialize(to_deserialize)

    def _create_deserializer_of_type_with_cache(self, deserializer_type: Type) -> "Deserializer":
        """
        Creates a deserializer of the given type, exploiting a cache.
        :param deserializer_type: the type of deserializer to create
        :return: the deserializer
        """
        if deserializer_type not in self._deserializers_cache:
            self._deserializers_cache[deserializer_type] = self._create_deserializer_of_type(deserializer_type)
        return self._deserializers_cache[deserializer_type]
