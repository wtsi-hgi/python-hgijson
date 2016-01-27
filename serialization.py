from abc import ABCMeta, abstractmethod
from typing import Any, TypeVar, Generic, Iterable, Container, List, Tuple
from typing import Dict

from hgicommon.serialization.json.temp import PrimitiveJsonSerializableType

SerializableType = TypeVar("Serializable")

PrimitiveUnionType = TypeVar("PrimitiveUnion")


class Serializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    TODO
    """
    # def __init__(self, property_mappings: Iterable[PropertyMapping], *args, **kwargs):
    def __init__(self, property_mappings: Iterable[Any], *args, **kwargs):
        """
        TODO
        :param primitive_types:
        :param property_mappings:
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self._property_mappings = property_mappings
        self._serializers_cache = dict()    # type: Dict[type, Serializer]

    def serialize(self, serializable: SerializableType) -> PrimitiveUnionType:
        """
        Serializes the given serializable object.
        :param serializable: the object to serialize
        :return: a serialization of the given object
        """
        serialized = self._create_serialized_container()

        for mapping in self._property_mappings:
            if mapping.object_property_setter is not None and mapping.serialized_property_setter is not None:
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
        TODO
        :return:
        """
        pass


class Deserializer(Generic[SerializableType, PrimitiveUnionType], metaclass=ABCMeta):
    """
    TODO
    """
    # TODO: Order parameters same as serializer
    # def __init__(self, deserializable_cls: type, property_mappings: Iterable[PropertyMapping], *args, **kwargs):
    def __init__(self, deserializable_cls: type, property_mappings: Iterable[Any], *args, **kwargs):
        """
        TODO
        :param primitive_types:
        :param deserializable_cls:
        :param property_mappings:
        """
        super().__init__(*args, **kwargs)
        self._deserializable_cls = deserializable_cls
        self._property_mappings = property_mappings
        self._deserializers_cache = dict()    # type: Dict[type, Deserializer]

    def deserialize(self, object_as_json: PrimitiveJsonSerializableType) -> SerializableType:
        """
        TODO
        :param object_as_json:
        :return:
        """
        mappings_not_set_in_constructor = []

        init_kwargs = dict()    # Dict[str, Any]
        for mapping in self._property_mappings:
            if mapping.constructor_parameter_name is not None:
                assert mapping.serialized_property_getter is not None
                value = mapping.serialized_property_getter(object_as_json)
                decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
                init_kwargs[mapping.constructor_parameter_name] = decoded_value
            else:
                mappings_not_set_in_constructor.append(mapping)

        decoded = self._deserializable_cls(**init_kwargs)

        for mapping in mappings_not_set_in_constructor:
            assert mapping.constructor_parameter_name is None
            if mapping.serialized_property_getter is not None and mapping.object_property_setter is not None:
                value = mapping.serialized_property_getter(object_as_json)
                decoded_value = self._deserialize_property_value(value, mapping.deserializer_cls)
                mapping.object_property_setter(decoded, decoded_value)

        return decoded

    def _deserialize_property_value(self, value: PrimitiveJsonSerializableType, deserializer_type: type) -> Any:
        """
        Deserialize the given value using a deserializer of the given type.
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
        TODO
        :param deserializer_type:
        :return:
        """
        pass


class PrimitiveSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__((), *args, **kwargs)

    def serialize(self, serializable: Any):
        return serializable

    def _create_serializer_of_type(self, serializer_type: type):
        assert False

    def _create_serialized_container(self) -> Any:
        assert False


class PrimitiveDeserializer(Deserializer):
    def __init__(self, *args, **kwargs):
        super().__init__(Any, (), *args, **kwargs)

    def deserialize(self, object_as_json: PrimitiveJsonSerializableType):
        return object_as_json

    def _create_deserializer_of_type(self, deserializer_type: type):
        assert False

