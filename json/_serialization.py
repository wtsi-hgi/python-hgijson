from abc import ABCMeta, abstractmethod
from json import JSONEncoder, JSONDecoder
from typing import Dict, Union, Iterable, Sequence

import collections

from hgicommon.serialization.json.models import JsonPropertyMapping
from hgicommon.serialization.serialization import Serializer, Deserializer
from hgicommon.serialization.types import PrimitiveJsonSerializableType, SerializableType


class _JsonSerializer(Serializer):
    """
    TODO
    """
    _JSON_ENCODER_ARGS = []
    _JSON_ENCODER_KWARGS = {}

    def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
        return serializer_type(*self._JSON_ENCODER_ARGS, **self._JSON_ENCODER_KWARGS)

    def _create_serialized_container(self) -> Dict:
        return {}


class _JsonDeserializer(Deserializer):
    """
    TODO
    """
    _JSON_ENCODER_ARGS = []
    _JSON_ENCODER_KWARGS = {}

    def _create_deserializer_of_type(self, deserializer_type: type) -> Deserializer:
        return deserializer_type(*self._JSON_ENCODER_ARGS, **self._JSON_ENCODER_KWARGS)

    def _decode_json_as_dict(self, object_as_dict: dict) -> SerializableType:
        return self.deserialize(object_as_dict)


class MappingJSONEncoder(JSONEncoder, metaclass=ABCMeta):
    """
    JSON encoder that serialises an object based on a mapping of its properties to JSON properties.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    encoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        # FIXME: Create serializer here?
        self._serializer_cache = None

    def default(self, serializable: Union[SerializableType, Sequence[SerializableType]]) -> PrimitiveJsonSerializableType:
        serializer = self._create_serializer()

        if isinstance(serializable, collections.Iterable):
            if len(serializable) == 0:
                return []
            encoded = []
            for to_encode in serializable:
                encoded.append(serializer.serialize(to_encode))
            return encoded

        elif not isinstance(serializable, self._get_serializable_cls()):
            JSONEncoder.default(self, serializable)

        else:
            return serializer.serialize(serializable)

    def _create_serializer(self) -> _JsonSerializer:
        """
        TODO
        :return:
        """
        if self._serializer_cache is None:
            serializer_cls = type(
                "%sInternalSerializer" % type(self),
                (_JsonSerializer, ),
                {
                    "_JSON_ENCODER_ARGS": self._args,
                    "_JSON_ENCODER_KWARGS": self._kwargs
                }
            )
            self._serializer_cache = serializer_cls(self._get_property_mappings())
        return self._serializer_cache

    @abstractmethod
    def _get_property_mappings(self) -> Iterable[JsonPropertyMapping]:
        """
        TODO
        :return:
        """
        pass

    @abstractmethod
    def _get_serializable_cls(self) -> type:
        """
        TODO
        :return:
        """
        pass


class MappingJSONDecoder(JSONDecoder, metaclass=ABCMeta):
    """
    JSON decoder that creates an object from JSON based on a mapping from the JSON properties to the object properties,
    mindful that some properties may have to be passed through the constructor.

    Can decode collections of the deserializable object.

    As `json.dumps` requires a type rather than an instance and there is no control given over the instatiation, the
    decoded class and the mappings between the object properties and the json properties cannot be passed through the
    constructor. Instead this class must be subclassed and the subclass must define the relevant constants.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._deserializer_cache = None

    def decode(self, json_as_string: str, **kwargs) -> SerializableType:
        parsed_json = super().decode(json_as_string)
        deserializer = self._create_deserializer()

        if isinstance(parsed_json, list):
            decoded = []
            for instance_as_json in parsed_json:
                decoded.append(deserializer._decode_json_as_dict(instance_as_json))
            return decoded

        return deserializer._decode_json_as_dict(parsed_json)

    def _create_deserializer(self) -> _JsonDeserializer:
        """
        TODO
        :return:
        """
        if self._deserializer_cache is None:
            deserializer_cls = type(
                "%sInternalDeserializer" % type(self),
                (_JsonDeserializer, ),
                {
                    "_JSON_ENCODER_ARGS": self._args,
                    "_JSON_ENCODER_KWARGS": self._kwargs
                }
            )
            self._deserializer_cache = deserializer_cls(self._get_property_mappings(), self._get_deserializable_cls())
        return self._deserializer_cache

    @abstractmethod
    def _get_property_mappings(self) -> Iterable[JsonPropertyMapping]:
        """
        TODO
        :return:
        """
        pass

    @abstractmethod
    def _get_deserializable_cls(self) -> type:
        """
        TODO
        :return:
        """
        pass
