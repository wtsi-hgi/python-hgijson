from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Iterable, Dict

from hgicommon.serialization.types import SerializableType, PrimitiveUnionType, PrimitiveJsonSerializableType


class Serializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    Serializer that uses a mapping that describes how the process should occur for the type of serializable object that
    this serializer handles.
    """
    # TODO: Correct type hinting in signature without causing a cyclic dependency issue
    # def __init__(self, property_mappings: Iterable[PropertyMapping], *args, **kwargs):
    def __init__(self, property_mappings: Iterable[Any], *args, **kwargs):
        """
        Constructor.
        :param property_mappings: the property mappings to use during serialization
        """
        super().__init__()
        self._property_mappings = property_mappings     # type_but_do_not_import: Iterable[PropertyMapping]
        self._serializers_cache = dict()    # type: Dict[type, Serializer]

    def serialize(self, serializable: SerializableType) -> PrimitiveUnionType:
        """
        Serializes the given serializable object.
        :param serializable: the object to serialize
        :return: a serialization of the given object
        """
        serialized = self._create_serialized_container()

        for mapping in self._property_mappings:
            if mapping.object_property_getter is not None and mapping.serialized_property_setter is not None:
                value = mapping.object_property_getter(serializable)
                encoded_value = self._serialize_property_value(value, mapping.serializer_cls)
                mapping.serialized_property_setter(serialized, encoded_value)

        return serialized

    def _serialize_property_value(self, value: Any, serializer_type: type) -> PrimitiveUnionType:
        """
        Serialize the given value using an serializer of the given type.
        :param value: the value to serialize
        :param serializer_type: the type of serializer to serialize the value with
        :return: serialized value
        """
        if serializer_type not in self._serializers_cache:
            self._serializers_cache[serializer_type] = self._create_serializer_of_type(serializer_type)

        serializer = self._serializers_cache[serializer_type]
        return serializer.serialize(value)

    @abstractmethod
    # FIXME: Signature should be self referential to this class:
    # def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
    def _create_serializer_of_type(self, serializer_type: type):
        """
        Create an instance of an serializer of the given type.
        :param serializer_type: the type of serializer to instantiate (a subclass of `Serializer`)
        :return: the created serializer
        """
        pass

    @abstractmethod
    def _create_serialized_container(self) -> Any:
        """
        Create the container in which serialized representation is built in
        :return: the container
        """
        pass


class Deserializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    Deserializer that uses a mapping that describes how the process should occur for the type of deserializable object
    that this deserializer handles.
    """
    # TODO: Correct type hinting in signature without causing a cyclic dependency issue
    # def __init__(self, deserializable_cls: type, property_mappings: Iterable[PropertyMapping], *args, **kwargs):
    def __init__(self, property_mappings: Iterable[Any], deserializable_cls: type, *args, **kwargs):
        """
        Construtor.
        :param property_mappings: the property mappings that this deserialiser uses when deserialing an object
        :param deserializable_cls: the class that should be built as a result of deserialization
        """
        super().__init__()
        self._property_mappings = property_mappings     # type_but_do_not_import: Iterable[PropertyMapping]
        self._deserializable_cls = deserializable_cls
        self._deserializers_cache = dict()    # type: Dict[type, Deserializer]

    def deserialize(self, object_property_value_dict: PrimitiveJsonSerializableType) -> SerializableType:
        """
        Deserializes the given representation of the serialized object.
        :param object_property_value_dict: the serialized object as a dictionary
        :return: the deserialized object
        """
        mappings_not_set_in_constructor = []

        init_kwargs = dict()    # Dict[str, Any]
        for mapping in self._property_mappings:
            if mapping.object_constructor_parameter_name is not None:
                assert mapping.serialized_property_getter is not None
                value = mapping.serialized_property_getter(object_property_value_dict)
                decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
                init_kwargs[mapping.object_constructor_parameter_name] = decoded_value
            else:
                mappings_not_set_in_constructor.append(mapping)

        decoded = self._deserializable_cls(**init_kwargs)

        for mapping in mappings_not_set_in_constructor:
            assert mapping.object_constructor_parameter_name is None
            if mapping.serialized_property_getter is not None and mapping.object_property_setter is not None:
                value = mapping.serialized_property_getter(object_property_value_dict)
                decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
                mapping.object_property_setter(decoded, decoded_value)

        assert type(decoded) == self._deserializable_cls
        return decoded

    def _deserialize_property_value(self, value: PrimitiveJsonSerializableType, deserializer_type: type) -> Any:
        """
        Deserializes the given value using a deserializer of the given type.
        :param value: the value to deserialize
        :param deserializer_type: the type of deserializer to deserialize the value with
        :return: deserialized value
        """
        if deserializer_type not in self._deserializers_cache:
            self._deserializers_cache[deserializer_type] = self._create_deserializer_of_type(deserializer_type)

        deserializer = self._deserializers_cache[deserializer_type]
        return deserializer.deserialize(value)

    @abstractmethod
    def _create_deserializer_of_type(self, deserializer_type: type):
        """
        Creates a deserializer of the given type.
        :param deserializer_type: the type of deserializer to create
        :return: the created deserializer (of type `Deserializer`)
        """
        pass
