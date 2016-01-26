from abc import ABCMeta
from typing import Iterable

from hgicommon.serialization.json.common import JsonPropertyMapping
from hgicommon.serialization.json.decoders import _MappingJSONDecoder, _CollectionMappingJSONDecoder
from hgicommon.serialization.json.encoders import _MappingJSONEncoder, _CollectionMappingJSONEncoder


class _JSONSerializationClassBuilder(metaclass=ABCMeta):
    """
    TODO
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(), iterable: bool=False):
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
        cls_name = "%sJSONEncoder" % self.target_cls.__name__
        encoder_base_cls = _MappingJSONEncoder if not self.iterable else _CollectionMappingJSONEncoder
        return type(
            cls_name,
            (encoder_base_cls, ),
            {
                "ENCODING_CLS": self.target_cls,
                "PROPERTY_MAPPINGS": self.mappings
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
        class_name = "%sJSONDecoder" % self.target_cls.__name__
        decoder_base_cls = _MappingJSONDecoder if not self.iterable else _CollectionMappingJSONDecoder
        return type(
            class_name,
            (decoder_base_cls, ),
            {
                "DECODING_CLS": self.target_cls,
                "PROPERTY_MAPPINGS": self.mappings
            }
        )
