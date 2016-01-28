from abc import ABCMeta
from typing import Iterable, TypeVar

from hgicommon.serialization.models import PropertyMapping
from hgicommon.serialization.json.decoders import _MappingJSONDecoder, _CollectionMappingJSONDecoder
from hgicommon.serialization.json.encoders import _MappingJSONEncoder, _CollectionMappingJSONEncoder
from hgicommon.serialization.types import PrimitiveJsonSerializableType


class _JSONSerializationClassBuilder(metaclass=ABCMeta):
    """
    TODO
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[PropertyMapping]=(), iterable: bool=False):
        self.target_cls = target_cls
        self.mappings = mappings
        self.iterable = iterable


class MappingJSONEncoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `_MappingJSONEncoder` concrete subclasses.
    """
    def build(self) -> type:
        """
        Build a subclass of `_MappingJSONEncoder`.
        :return: the built subclass
        """
        cls_name = "%sDynamicMappingJSONEncoder" % self.target_cls.__name__
        encoder_base_cls = _MappingJSONEncoder if not self.iterable else _CollectionMappingJSONEncoder
        return type(
            cls_name,
            (encoder_base_cls[TypeVar("T", bound=self.target_cls), PrimitiveJsonSerializableType], ),
            {
                "_SERIALIZABLE_CLS": self.target_cls,
                "_PROPERTY_MAPPINGS": self.mappings
            }
        )


class MappingJSONDecoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `_MappingJSONDecoder` concrete subclasses.
    """
    def build(self) -> type:
        """
        Build a subclass of `_MappingJSONDecoder`.
        :return: the built subclass
        """
        class_name = "%sDynamicMappingJSONDecoder" % self.target_cls.__name__
        decoder_base_cls = _MappingJSONDecoder if not self.iterable else _CollectionMappingJSONDecoder
        return type(
            class_name,
            (decoder_base_cls[TypeVar("T", bound=self.target_cls), PrimitiveJsonSerializableType], ),
            {
                "_DESERIALIZABLE_CLS": self.target_cls,
                "_PROPERTY_MAPPINGS": self.mappings
            }
        )
