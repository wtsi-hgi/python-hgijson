from typing import Dict

from hgijson.serialization import Serializer, Deserializer


class JsonObjectSerializer(Serializer):
    """
    JSON serializer for models represented by {}.
    """
    _JSON_ENCODER_ARGS = []
    _JSON_ENCODER_KWARGS = {}

    def _create_serializer_of_type(self, serializer_type: type) -> Serializer:
        return serializer_type(*self._JSON_ENCODER_ARGS, **self._JSON_ENCODER_KWARGS)

    def _create_serialized_container(self) -> Dict:
        return {}


class JsonObjectDeserializer(Deserializer):
    """
    JSON deserializer for models represented by {}.
    """
    _JSON_ENCODER_ARGS = []
    _JSON_ENCODER_KWARGS = {}

    def _create_deserializer_of_type(self, deserializer_type: type) -> Deserializer:
        return deserializer_type(*self._JSON_ENCODER_ARGS, **self._JSON_ENCODER_KWARGS)
