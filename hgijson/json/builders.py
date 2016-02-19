from abc import ABCMeta
from json import encoder
from typing import Iterable, List, Tuple

from hgijson.json._serialization import MappingJSONEncoder, MappingJSONDecoder, PropertyMapper
from hgijson.json.models import JsonPropertyMapping


def _get_all_property_mappings(property_mapper: PropertyMapper, property_mappings: Iterable[JsonPropertyMapping],
                               superclasses: Tuple[type]) -> Iterable[JsonPropertyMapping]:
    """
    TODO
    :param property_mapper:
    :param property_mappings:
    :param superclasses:
    :return:
    """
    mappings = []
    for superclass in superclasses:
        if superclass != MappingJSONEncoder:
            super_mappings = superclass._get_property_mappings(property_mapper)
            mappings.extend(super_mappings)

    # FIXME: Favour subclass mappings for constructor! Also ensure evaluated in order (superclass' first)
    mappings.extend(property_mappings)
    return mappings


class _JSONSerializationClassBuilder(metaclass=ABCMeta):
    """
    Subclass of serialization class builders.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(),
                 superclasses: Tuple=None):
        """
        Constructor.
        :param superclasses: the superclasses to which the serialization class should extend
        :param target_cls: the class that the builder targets
        :param mappings: mappings from JSON properties to object properties
        """
        self.superclasses = superclasses
        self.target_cls = target_cls
        self.mappings = mappings


class MappingJSONEncoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `MappingJSONEncoder` concrete subclasses.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(),
                 superclasses: Tuple=(MappingJSONEncoder, )):
        super().__init__(target_cls, mappings, superclasses)

    def build(self) -> type:
        """
        Build a subclass of `MappingJSONEncoder`.
        :return: the built subclass
        """
        def _get_property_mappings(encoder: MappingJSONEncoder) -> Iterable[JsonPropertyMapping]:
            return _get_all_property_mappings(encoder, self.mappings, self.superclasses)

        def get_serializable_cls(encoder: MappingJSONEncoder) -> type:
            return self.target_cls

        def default(encoder: MappingJSONEncoder, *args, **kwargs):
            # Sort subclasses so subclass' default method is called last
            superclasses_as_list = list(self.superclasses)
            superclasses_as_list.sort(key=lambda superclass: 1 if superclass == MappingJSONEncoder else -1)

            encoded_combined = {}
            for superclass in superclasses_as_list:
                encoded = superclass.default(encoder, *args, **kwargs)
                encoded_combined.update(encoded)

            return encoded_combined

        return type(
            "%sDynamicMappingJSONEncoder" % self.target_cls.__name__,
            self.superclasses,
            {
                "_get_property_mappings": _get_property_mappings,
                "_get_serializable_cls": get_serializable_cls,
                "default": default
            }
        )


class MappingJSONDecoderClassBuilder(_JSONSerializationClassBuilder):
    """
    Builder for `MappingJSONDecoder` concrete subclasses.
    """
    def __init__(self, target_cls: type=type(None), mappings: Iterable[JsonPropertyMapping]=(),
                 superclasses: Tuple=(MappingJSONDecoder, )):
        super().__init__(target_cls, mappings, superclasses)

    def build(self) -> type:
        """
        Build a subclass of `MappingJSONDecoder`.
        :return: the built subclass
        """
        def _get_property_mappings(encoder: MappingJSONEncoder) -> Iterable[JsonPropertyMapping]:
            return _get_all_property_mappings(encoder, self.mappings, self.superclasses)

        def get_deserializable_cls(decoder: MappingJSONDecoder) -> type:
            return self.target_cls

        return type(
            "%sDynamicMappingJSONDecoder" % self.target_cls.__name__,
            self.superclasses,
            {
                "_get_property_mappings": _get_property_mappings,
                "_get_deserializable_cls": get_deserializable_cls
            }
        )
