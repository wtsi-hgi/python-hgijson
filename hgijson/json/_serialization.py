from abc import ABCMeta, abstractmethod
from json import JSONEncoder, JSONDecoder
from typing import Union, Sequence, List

from hgijson.json._serializers import JsonObjectSerializer, JsonObjectDeserializer
from hgijson.json.interfaces import ParsedJSONDecoder
from hgijson.models import PropertyMapping
from hgijson.types import PrimitiveJsonSerializableType, SerializableType


class PropertyMapper(metaclass=ABCMeta):
    """
    Model of a mapping from a property of a JSON model to a property of a native Python object.
    """
    def _get_property_mappings(self) -> List[PropertyMapping]:
        """
        Gets the property mappings that are to be used in this encoder.
        :return: the property mappings to use in the order in which they should be applied
        """
        return []


class MappingJSONEncoder(JSONEncoder, PropertyMapper, metaclass=ABCMeta):
    """
    JSON encoder that serialises an object based on a mapping of its properties to JSON properties.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    encoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    @abstractmethod
    def _get_serializable_cls(self) -> type:
        """
        Gets the type of class that this encoder will serialize.
        :return: the class the encoder will serialize
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._serializer_cache = None

    def default(self, serializable: Union[SerializableType, Sequence[SerializableType]]) \
            -> PrimitiveJsonSerializableType:
        serializer = self._create_serializer()
        if not isinstance(serializable, List) and not isinstance(serializable, self._get_serializable_cls()):
            return super().default(serializable)

        return serializer.serialize(serializable)

    def _create_serializer(self) -> JsonObjectSerializer:
        """
        Create serializer that is to be used by this encoder
        :return: the serializer
        """
        if self._serializer_cache is None:
            serializer_cls = type(
                "%sInternalSerializer" % type(self),
                (JsonObjectSerializer,),
                {
                    "_JSON_ENCODER_ARGS": self._args,
                    "_JSON_ENCODER_KWARGS": self._kwargs
                }
            )
            self._serializer_cache = serializer_cls(self._get_property_mappings())
        return self._serializer_cache


class MappingJSONDecoder(JSONDecoder, ParsedJSONDecoder, PropertyMapper, metaclass=ABCMeta):
    """
    JSON decoder that creates an object from JSON based on a mapping from the JSON properties to the object properties,
    mindful that some properties may have to be passed through the constructor.

    Can decode collections of the deserializable object.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    decoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    @abstractmethod
    def _get_deserializable_cls(self) -> type:
        """
        Gets the type of class that this decoder will deserialize.
        :return: the class the decoder will deserialize
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._deserializer_cache = None

    def decode(self, json_as_string: str, **kwargs) -> SerializableType:
        json_as_dict = super().decode(json_as_string)
        return self.decode_parsed(json_as_dict)

    def decode_parsed(self, parsed_json: PrimitiveJsonSerializableType) -> SerializableType:
        deserializer = self._create_deserializer()
        return deserializer.deserialize(parsed_json)

    def _create_deserializer(self) -> JsonObjectDeserializer:
        """
        Creates a deserializer that is to be used by this decoder.
        :return: the deserializer
        """
        if self._deserializer_cache is None:
            deserializer_cls = type(
                "%sInternalDeserializer" % type(self),
                (JsonObjectDeserializer,),
                {
                    "_JSON_ENCODER_ARGS": self._args,
                    "_JSON_ENCODER_KWARGS": self._kwargs
                }
            )
            self._deserializer_cache = deserializer_cls(self._get_property_mappings(), self._get_deserializable_cls())
        return self._deserializer_cache
