from abc import ABCMeta
from typing import Iterable, TypeVar

from hgicommon.serialization.json._serialization import MappingJSONEncoder, MappingJSONDecoder
from hgicommon.serialization.json.models import JsonPropertyMapping
from hgicommon.serialization.types import PrimitiveJsonSerializableType


class _JSONSerializationClassBuilder(metaclass=ABCMeta):
    """
    Subclass of serialization class builders.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=()):
        """
        Constructor.
        :param target_cls: the class that the builder targets
        :param mappings: mappings from JSON properties to object properties
        """
        self.target_cls = target_cls
        self.mappings = mappings


class MappingJSONEncoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `MappingJSONEncoder` concrete subclasses.
    """
    def build(self) -> type:
        """
        Build a subclass of `MappingJSONEncoder`.
        :return: the built subclass
        """
        cls_name = "%sDynamicMappingJSONEncoder" % self.target_cls.__name__
        return type(
            cls_name,
            (MappingJSONEncoder[TypeVar("T", bound=self.target_cls), PrimitiveJsonSerializableType], ),
            {
                "_SERIALIZABLE_CLS": self.target_cls,
                "_PROPERTY_MAPPINGS": self.mappings
            }
        )


class MappingJSONDecoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `MappingJSONDecoder` concrete subclasses.
    """
    def build(self) -> type:
        """
        Build a subclass of `MappingJSONDecoder`.
        :return: the built subclass
        """
        class_name = "%sDynamicMappingJSONDecoder" % self.target_cls.__name__
        return type(
            class_name,
            (MappingJSONDecoder[TypeVar("T", bound=self.target_cls), PrimitiveJsonSerializableType], ),
            {
                "_DESERIALIZABLE_CLS": self.target_cls,
                "_PROPERTY_MAPPINGS": self.mappings
            }
        )
