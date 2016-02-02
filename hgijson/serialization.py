from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Iterable
from typing import Dict

from hgijson.types import SerializableType, PrimitiveUnionType, PrimitiveJsonSerializableType


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
                serializer = self._create_serializer_with_cache(mapping.serializer_cls)
                encoded_value = self._serialize_property_value(value, serializer)
                mapping.serialized_property_setter(serialized, encoded_value)

        return serialized

    # TODO: Fix self-referential signature
    def _serialize_property_value(self, to_serialize: Any, serializer) -> Any:
        """
        Serializes the given value using the given serializer.
        :param to_serialize: the value to deserialize
        :param serializer: the serializer to serialize the value with
        :return: serialized value
        """
        assert serializer is not None
        if isinstance(to_serialize, list):
            return self._serialize_property_value_list(to_serialize, serializer)
        elif isinstance(to_serialize, dict):
            return self._serialize_property_value_dict(to_serialize, serializer)
        else:
            return serializer.serialize(to_serialize)

    # TODO: Fix self-referential signature
    def _serialize_property_value_list(self, to_serialize: list, serializer) -> Any:
        """
        Serializes the given value using the given serializer.
        :param to_serialize: the value to serialize
        :param serializer: the serializer to serialize the value with
        :return: serialized value
        """
        serialized = []
        for item in to_serialize:
            serialized.append(serializer.serialize(item))
        return serialized

    # TODO: Fix self-referential signature
    def _serialize_property_value_dict(self, to_serialize: dict, serializer) -> Any:
        """
        Serializes the given value using the given serializer.
        :param to_serialize: the value to serialize
        :param serializer: the serializer to serialize the value with
        :return: serialized value
        """
        serialized = {}
        for key, value in to_serialize.items():
            # Not automatically supporting complex keys!
            serialized[key] = serializer.serialize(value)
        return serialized


    @abstractmethod
    def _create_serialized_container(self) -> Any:
        """
        Create the container in which serialized representation is built in
        :return: the container
        """
        pass

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

    # TODO: Fix self-referential signature
    def _create_serializer_with_cache(self, serializer_type: type):
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
    def __init__(self, property_mappings: Iterable[Any], deserializable_cls: type):
        """
        Constructor.
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

        init_kwargs = dict()    # type: Dict[str, Any]
        for mapping in self._property_mappings:
            if mapping.object_constructor_parameter_name is not None:
                assert mapping.serialized_property_getter is not None
                assert mapping.object_constructor_argument_modifier is not None
                value = mapping.serialized_property_getter(object_property_value_dict)
                deserializer = self._create_deserializer_with_cache(mapping.deserializer_cls)
                decoded_value = self._deserialize_property_value(value, deserializer)
                argument = mapping.object_constructor_argument_modifier(decoded_value)
                init_kwargs[mapping.object_constructor_parameter_name] = argument
            else:
                mappings_not_set_in_constructor.append(mapping)

        decoded = self._deserializable_cls(**init_kwargs)
        assert type(decoded) == self._deserializable_cls

        for mapping in mappings_not_set_in_constructor:
            assert mapping.object_constructor_parameter_name is None
            if mapping.serialized_property_getter is not None and mapping.object_property_setter is not None:
                value = mapping.serialized_property_getter(object_property_value_dict)
                deserializer = self._create_deserializer_with_cache(mapping.deserializer_cls)
                decoded_value = self._deserialize_property_value(value, deserializer)
                mapping.object_property_setter(decoded, decoded_value)

        return decoded

    # TODO: Fix self-referential signature
    def _deserialize_property_value(self, to_deserialize: PrimitiveJsonSerializableType, deserializer) -> Any:
        """
        Deserializes the given value using the given deserializer.
        :param to_deserialize: the value to deserialize
        :param deserializer: the deserializer to deserialize the value with
        :return: deserialized value
        """
        assert deserializer is not None
        if isinstance(to_deserialize, list):
            return self._deserialize_property_value_list(to_deserialize, deserializer)
        elif isinstance(to_deserialize, dict):
            return self._deserialize_property_value_dict(to_deserialize, deserializer)
        else:
            return deserializer.deserialize(to_deserialize)

    # TODO: Fix self-referential signature
    def _deserialize_property_value_list(self, to_deserialize: list, deserializer) -> Any:
        """
        Deserializes the given value using the given deserializer.
        :param to_deserialize: the value to deserialize
        :param deserializer: the deserializer to deserialize the value with
        :return: deserialized value
        """
        deserialized = []
        for item in to_deserialize:
            deserialized.append(deserializer.deserialize(item))
        return deserialized

    # TODO: Fix self-referential signature
    def _deserialize_property_value_dict(self, to_deserialize: dict, deserializer) -> Any:
        """
        Deserializes the given value using the given deserializer.
        :param to_deserialize: the value to deserialize
        :param deserializer: the deserializer to deserialize the value with
        :return: deserialized value
        """
        deserialized = {}
        for key, value in to_deserialize.items():
            # Not automatically supporting complex keys!
            deserialized[key] = deserializer.deserialize(value)
        return deserialized

    @abstractmethod
    def _create_deserializer_of_type(self, deserializer_type: type):
        """
        Creates a deserializer of the given type.
        :param deserializer_type: the type of deserializer to create
        :return: the created deserializer (of type `Deserializer`)
        """
        pass

    # TODO: Fix self-referential signature
    def _create_deserializer_with_cache(self, deserializer_type: type):
        """
        Creates a deserializer of the given type, exploiting a cache.
        :param deserializer_type: the type of deserializer to create
        :return: the deserializer
        """
        if deserializer_type not in self._deserializers_cache:
            self._deserializers_cache[deserializer_type] = self._create_deserializer_of_type(deserializer_type)
        return self._deserializers_cache[deserializer_type]
