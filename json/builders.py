from abc import ABCMeta
from typing import Iterable, TypeVar

from hgicommon.serialization.json.common import JsonPropertyMapping
from hgicommon.serialization.json.decoders import _MappingJSONDecoder
from hgicommon.serialization.json.encoders import _MappingJSONEncoder


# Type of a concrete subclass of `_MappingJSONEncoder`, created dynamically.
MappingJSONEncoderType = TypeVar("MappingJSONEncoder", bound=_MappingJSONEncoder)

# Type of a concrete subclass of `_MappingJSONDecoder`, created dynamically.
MappingJSONDecoderType = TypeVar("MappingJSONDecoder", bound=_MappingJSONDecoder)


class _JSONSerializationClassBuilder(metaclass=ABCMeta):
    """
    TODO
    """
    def __init__(self):
        self._target_cls = type(None)
        self._mappings = []

    @property
    def target_cls(self) -> type:
        return self._target_cls

    @target_cls.setter
    def target_cls(self, cls: type):
        self._target_cls = cls

    @property
    def mappings(self) -> Iterable[JsonPropertyMapping]:
        return self._mappings

    @mappings.setter
    def mappings(self, mappings: Iterable[JsonPropertyMapping]):
        self._mappings = mappings


class MappingJSONEncoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `_MappingJSONEncoder` concrete subclasses.
    """
    def build(self) -> MappingJSONEncoderType:
        """
        Build a subclass of `_MappingJSONEncoder`.
        :return: the built subclass
        """
        class_name = "%sJSONEncoder" % self.target_cls.__name__
        return type(
            class_name,
            (_MappingJSONEncoder, ),
            {
                "ENCODING_CLS": self.target_cls,
                "PROPERTY_MAPPINGS": self.mappings
            }
        )


class MappingJSONDecoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `_MappingJSONDecoder` concrete subclasses.
    """
    def build(self) -> MappingJSONDecoderType:
        """
        Build a subclass of `_MappingJSONDecoder`.
        :return: the built subclass
        """
        class_name = "%sJSONDecoder" % self.target_cls.__name__
        return type(
            class_name,
            (_MappingJSONDecoder, ),
            {
                "DECODING_CLS": self.target_cls,
                "PROPERTY_MAPPINGS": self.mappings
            }
        )
