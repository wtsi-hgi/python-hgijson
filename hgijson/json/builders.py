from abc import ABCMeta
from typing import Iterable, Tuple, List

from hgijson.json._serialization import MappingJSONEncoder, MappingJSONDecoder, PropertyMapper
from hgijson.json.models import JsonPropertyMapping
from hgijson.json.primitive import SetJSONEncoder, SetJSONDecoder


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


def _get_all_property_mappings(encoder: MappingJSONEncoder, property_mappings: Iterable[JsonPropertyMapping],
                               superclasses: Tuple[PropertyMapper]) -> List[JsonPropertyMapping]:
    """
    Gets all of the property mappings from the given property mapper, considering the property mappings for self and the
    property mappings defined by the superclass.
    :param encoder: `self` when binded as class method
    :param property_mappings: mappings defined for the given encoder, excluding mappings defined by superclasses
    :param superclasses: superclasses of the given encoder. Property mappers in later superclasses may override the
    effects of property mappers defined by superclasses closer to the start of the list
    :return: all of the property mappings for the given encoder
    """
    mappings = []
    for superclass in superclasses:
        super_mappings = superclass._get_property_mappings(superclass)
        mappings.extend(super_mappings)

    # Add property mappings of own to end of the mappings list
    mappings.extend(property_mappings)

    # Note: It is very difficult to cull all property mappers that target the same properties, leaving only the ones
    # from the lowest class in the hierarchy. This is because such mappers may be encoded as functions. Given that such
    # overloading is unlikely to be used much and the cost of doing a mapping and then mapping again over the top of it
    # will likely be small, there will be no attempt of such a cull.
    return mappings


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
        def _get_property_mappings(encoder: MappingJSONEncoder) -> List[JsonPropertyMapping]:
            return _get_all_property_mappings(encoder, self.mappings, self.superclasses)

        def get_serializable_cls(encoder: MappingJSONEncoder) -> type:
            return self.target_cls

        def default(encoder: MappingJSONEncoder, serializable):
            if isinstance(serializable, List):
                # Fix for #8
                return [encoder.default(item) for item in serializable]
            else:
                # Sort subclasses so subclass' default method is called last
                superclasses_as_list = list(self.superclasses)
                superclasses_as_list.sort(key=lambda superclass: 1 if superclass == MappingJSONEncoder else -1)

                encoded_combined = {}
                for superclass in superclasses_as_list:
                    encoded = superclass.default(encoder, serializable)
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
        def _get_property_mappings(encoder: MappingJSONEncoder) -> List[JsonPropertyMapping]:
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


class SetJSONEncoderClassBuilder:
    """
    Builder for `SetJSONEncoder` concrete subclasses.

    Required for: https://github.com/wtsi-hgi/python-json/issues/11.
    """
    def __init__(self, item_encoder_cls: type):
        """
        Constructor.
        :param item_encoder_cls: type of encoder for items in the set
        """
        self.item_encoder_cls = item_encoder_cls

    def build(self) -> type:
        """
        Build a subclass of `SetJSONEncoder`.
        :return: the built subclass
        """
        name = self.item_encoder_cls.__name__.replace("JSONEncoder", "")

        return type(
            "%sSetJSONEncoder" % name,
            (SetJSONEncoder, ),
            {
                "item_encoder_cls": self.item_encoder_cls,
            }
        )


class SetJSONDecoderClassBuilder:
    """
    Builder for `SetJSONDecoder` concrete subclasses.

    Required for: https://github.com/wtsi-hgi/python-json/issues/11.
    """
    def __init__(self, item_decoder_cls: type):
        """
        Constructor.
        :param item_decoder_cls: type of decoder for items in the set
        """
        self.item_decoder_cls = item_decoder_cls

    def build(self) -> type:
        """
        Build a subclass of `SetJSONDecoder`.
        :return: the built subclass
        """
        name = self.item_decoder_cls.__name__.replace("JSONDecoder", "")

        return type(
            "%sSetJSONDecoder" % name,
            (SetJSONDecoder, ),
            {
                "item_decoder_cls": self.item_decoder_cls,
            }
        )
