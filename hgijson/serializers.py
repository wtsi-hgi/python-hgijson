from typing import Any

from hgijson.serialization import Serializer, Deserializer
from hgijson.types import PrimitiveJsonSerializableType


class PrimitiveSerializer(Serializer):
    """
    Serializer for primitive values - just returns them.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(())

    def serialize(self, serializable: Any):
        return serializable

    def _create_serializer_of_type(self, serializer_type: type):
        """
        Unused - implemented to satisfy the interface only.
        """

    def _create_serialized_container(self) -> Any:
        """
        Unused - implemented to satisfy the interface only.
        """


class PrimitiveDeserializer(Deserializer):
    """
    Deserializer for primitive values - just returns them.
    """
    def __init__(self, *args, **kwargs):
        super().__init__((), object)

    def deserialize(self, object_property_value_dict: PrimitiveJsonSerializableType):
        return object_property_value_dict

    def _create_deserializer_of_type(self, deserializer_type: type):
        """
        Unused - implemented to satisfy the interface only.
        """
