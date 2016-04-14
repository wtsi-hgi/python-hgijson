from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Iterable, Union, Sequence, Dict, List

from hgijson.types import SerializableType, PrimitiveUnionType, PrimitiveJsonSerializableType


class Serializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    Serializer that uses a mapping that describes how the process should occur for the type of serializable object that
    this serializer handles.
    """
    # TODO: Correct type hinting in signature without causing a cyclic dependency issue
    @abstractmethod
    # def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
    def _create_serializer_of_type(self, serializer_type: type):
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

    def __init__(self, property_mappings: Iterable):
        """
        Constructor.
        :param property_mappings: TODO
        """
        self._property_mappings = property_mappings     # type_but_do_not_import: Iterable[PropertyMapping]
        self._serializers_cache = dict()    # type: Dict[type, Serializer]

    def serialize(self, serializable: Union[SerializableType, Sequence[SerializableType]]) -> PrimitiveUnionType:
        """
        Serializes the given serializable object or collection of serializable objects.
        :param serializable: the object to serialize
        :return: a serialization of the given object
        """
        if isinstance(serializable, List):
            return [self.serialize(item) for item in serializable]
        else:
            serialized = self._create_serialized_container()

            for mapping in self._property_mappings:
                if mapping.object_property_getter is not None and mapping.serialized_property_setter is not None:
                    value = mapping.object_property_getter(serializable)
                    if not (mapping.optional and value is None):
                        encoded_value = self._serialize_property_value(value, mapping.serializer_cls)
                        mapping.serialized_property_setter(serialized, encoded_value)

            return serialized

    def _serialize_property_value(self, to_serialize: Any, serializer_cls: type) -> Any:
        """
        Serializes the given value using the given serializer.
        :param to_serialize: the value to deserialize
        :param serializer_cls: the type of serializer to use
        :return: serialized value
        """
        serializer = self._create_serializer_of_type_with_cache(serializer_cls)
        assert serializer is not None
        return serializer.serialize(to_serialize)

    # TODO: Fix self-referential signature
    def _create_serializer_of_type_with_cache(self, serializer_type: type):
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
    def _create_deserializer_of_type(self, deserializer_type: type):
        """
        Creates a deserializer of the given type.
        :param deserializer_type: the type of deserializer to create
        :return: the created deserializer (of type `Deserializer`)
        """

    def __init__(self, property_mappings: Iterable, deserializable_cls: type):
        """
        Constructor.
        :param property_mappings: TODO
        :param deserializable_cls: the class that should be built as a result of deserialization
        """
        self._property_mappings = property_mappings     # type_but_do_not_import: Iterable[PropertyMapping]
        self._deserializable_cls = deserializable_cls
        self._deserializers_cache = dict()    # type: Dict[type, Deserializer]

    def deserialize(self, to_deserialize: PrimitiveJsonSerializableType) \
            -> Union[SerializableType, Sequence[SerializableType]]:
        """
        Deserializes the given representation of the serialized object.
        :param to_deserialize: the serialized object as a dictionary
        :return: the deserialized object or collection of deserialized objects
        """
        if isinstance(to_deserialize, list):
            deserialized = []
            for item in to_deserialize:
                item_deserialized = self.deserialize(item)
                deserialized.append(item_deserialized)
            return deserialized
        else:
            mappings_not_set_in_constructor = []    # type_but_do_not_import: List[PropertyMapping]

            init_kwargs = dict()    # type: Dict[str, Any]
            for mapping in self._property_mappings:
                if mapping.object_constructor_parameter_name is not None:
                    value = mapping.serialized_property_getter(to_deserialize)
                    if not (mapping.optional and value is None):
                        decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
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
                        mapping.object_property_setter(decoded, decoded_value)

            return decoded

    def _deserialize_property_value(self, to_deserialize: PrimitiveJsonSerializableType, deserializer_cls: type) -> Any:
        """
        Deserializes the given value using the given deserializer.
        :param to_deserialize: the value to deserialize
        :param deserializer_cls: the type of deserializer to use
        :return: deserialized value
        """
        deserializer = self._create_deserializer_of_type_with_cache(deserializer_cls)
        assert deserializer is not None
        return deserializer.deserialize(to_deserialize)

    # TODO: Fix self-referential signature
    def _create_deserializer_of_type_with_cache(self, deserializer_type: type):
        """
        Creates a deserializer of the given type, exploiting a cache.
        :param deserializer_type: the type of deserializer to create
        :return: the deserializer
        """
        if deserializer_type not in self._deserializers_cache:
            self._deserializers_cache[deserializer_type] = self._create_deserializer_of_type(deserializer_type)
        return self._deserializers_cache[deserializer_type]
