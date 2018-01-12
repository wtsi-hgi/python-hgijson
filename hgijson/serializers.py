from typing import Any

from hgijson.serialization import Serializer, Deserializer
from hgijson.custom_types import PrimitiveJsonType


class PrimitiveSerializer(Serializer):
    """
    Serializer for primitive values - just returns them.
    """
    def __init__(self, *args, **kwargs):
        super().__init__([])

    def serialize(self, serializable: Any) -> Any:
        return serializable

    def _create_serializer_of_type(self, serializer_type: type) -> None:
        """
        Unused - implemented to satisfy the interface only.
        """

    def _create_serialized_container(self) -> None:
        """
        Unused - implemented to satisfy the interface only.
        """


class PrimitiveDeserializer(Deserializer):
    """
    Deserializer for primitive values - just returns them.
    """
    def __init__(self, *args, **kwargs):
        super().__init__([], object)

    def deserialize(self, object_property_value_dict: PrimitiveJsonType) -> PrimitiveJsonType:
        return object_property_value_dict

    def _create_deserializer_of_type(self, deserializer_type: type) -> None:
        """
        Unused - implemented to satisfy the interface only.
        """
