from abc import ABCMeta
from typing import Iterable

from hgijson.json._serialization import MappingJSONEncoder, MappingJSONDecoder
from hgijson.json.models import JsonPropertyMapping


class _JSONSerializationClassBuilder(metaclass=ABCMeta):
    """
    Subclass of serialization class builders.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(), superclass: type=None):
        """
        Constructor.
        :param superclass: the superclass to which the serialization class should extend
        :param target_cls: the class that the builder targets
        :param mappings: mappings from JSON properties to object properties
        """
        self.superclass = superclass
        self.target_cls = target_cls
        self.mappings = mappings


class MappingJSONEncoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `MappingJSONEncoder` concrete subclasses.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(),
                 superclass: type=MappingJSONEncoder):
        super().__init__(target_cls, mappings, superclass)

    def build(self) -> type:
        """
        Build a subclass of `MappingJSONEncoder`.
        :return: the built subclass
        """
        def get_property_mappings(encoder: MappingJSONEncoder) -> Iterable[JsonPropertyMapping]:
            mappings = []
            if self.superclass != MappingJSONEncoder:
                super_mappings = self.superclass._get_property_mappings(encoder)
                mappings.extend(super_mappings)

            # FIXME: Favour subclass mappings!
            mappings.extend(self.mappings)
            return mappings

        def get_serializable_cls(encoder: MappingJSONEncoder) -> type:
            return self.target_cls

        def default(encoder: MappingJSONEncoder, *args, **kwargs):
            return self.superclass.default(encoder, *args, **kwargs)

        cls_name = "%sDynamicMappingJSONEncoder" % self.target_cls.__name__

        return type(
            cls_name,
            (self.superclass, ),
            {
                "_get_property_mappings": get_property_mappings,
                "_get_serializable_cls": get_serializable_cls,
                "default": default
            }
        )


class MappingJSONDecoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `MappingJSONDecoder` concrete subclasses.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(),
                 superclass: type=MappingJSONDecoder):
        super().__init__(target_cls, mappings, superclass)

    def build(self) -> type:
        """
        Build a subclass of `MappingJSONDecoder`.
        :return: the built subclass
        """
        def get_property_mappings(decoder: MappingJSONDecoder) -> Iterable[JsonPropertyMapping]:
            mappings = []
            if self.superclass != MappingJSONDecoder:
                super_mappings = self.superclass._get_property_mappings(decoder)
                mappings.extend(super_mappings)

            # FIXME: Favour subclass mappings!
            mappings.extend(self.mappings)
            return mappings

        def get_deserializable_cls(decoder: MappingJSONDecoder) -> type:
            return self.target_cls

        class_name = "%sDynamicMappingJSONDecoder" % self.target_cls.__name__

        return type(
            class_name,
            (self.superclass, ),
            {
                "_get_property_mappings": get_property_mappings,
                "_get_deserializable_cls": get_deserializable_cls
            }
        )
