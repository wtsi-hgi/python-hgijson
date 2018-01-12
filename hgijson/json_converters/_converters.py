import json
from abc import ABCMeta, abstractmethod
from json import JSONDecoder, JSONEncoder
from typing import Optional, Union, Callable, Type

from hgijson.json_converters.interfaces import ParsedJSONDecoder
from hgijson.serialization import Deserializer, Serializer
from hgijson.custom_types import PrimitiveJsonType, PrimitiveUnionType, SerializableType


class _JSONEncoderAsSerializer(Serializer, metaclass=ABCMeta):
    """
    JSON encoder wrapped to work as a `Serializer`.
    """
    @property
    @abstractmethod
    def encoder_type(self) -> Type[JSONEncoder]:
        """
        Gets the `JSONEncoder` type that is used by this serialiser.
        :return: the encoder type (must be a subclass of `JSONEncoder`)
        """

    def __init__(self, *args, **kwargs):
        super().__init__([])
        self._encoder = self.encoder_type(*args, **kwargs)

    def serialize(self, serializable: Optional[SerializableType]) -> PrimitiveUnionType:
        if type(self._encoder) == JSONEncoder:
            # Have to load from string to more rich representation - not possible to stop `encode` going to string :/
            return json.loads(self._encoder.encode(serializable))
        else:
            return self._encoder.default(serializable)

    def _create_serializer_of_type(self, serializer_type: Type[Serializer]) -> None:
        """
        Unused - implemented to satisfy the interface only.
        """

    def _create_serialized_container(self) -> None:
        """
        Unused - implemented to satisfy the interface only.
        """


class _JSONDecoderAsDeserializer(Deserializer, metaclass=ABCMeta):
    """
    JSON decoder wrapped to work as a `Deserializer`.
    """
    @property
    @abstractmethod
    def decoder_type(self) -> Type[JSONDecoder]:
        """
        Gets the `JSONDecoder` type that is used by this deserialiser.
        :return: the decoder type (must be a subclass of `JSONDecoder`)
        """

    def __init__(self, *args, **kwargs):
        super().__init__([], self.decoder_type)
        self._decoder = self.decoder_type(*args, **kwargs)

    def deserialize(self, deserializable: PrimitiveJsonType) -> Optional[SerializableType]:
        if not isinstance(self._decoder, ParsedJSONDecoder):
            # Decode must take a string (even though we have a richer representation) :/
            json_as_string = json.dumps(deserializable)
            return self._decoder.decode(json_as_string)
        else:
            # Optimisation - no need to convert our relatively rich representation into a string (just to turn it back
            # again!)
            return self._decoder.decode_parsed(deserializable)

    def _create_deserializer_of_type(self, deserializer_type: Type[JSONDecoder]) -> None:
        """
        Unused - implemented to satisfy the interface only.
        """


def json_encoder_to_serializer(encoder_cls: Union[Type[JSONEncoder], Callable[[], Type[JSONEncoder]]]) \
        -> Type[Serializer]:
    """
    Converts a `JSONEncoder` class into an equivalent `Serializer` class.
    :param encoder_cls: the encoder class type or a function that returns the type
    :return: the equivalent `Serializer` class
    """
    name = encoder_cls.__name__ if isinstance(encoder_cls, type) else "%sLambdaTypeReturn" % id(encoder_cls)
    return type(
        "%sAsSerializer" % name,
        (_JSONEncoderAsSerializer,),
        {
            "encoder_type": property(lambda self: encoder_cls if isinstance(encoder_cls, type) else encoder_cls())
        }
    )


def json_decoder_to_deserializer(decoder_cls: Union[Type[JSONDecoder], Callable[[], Type[JSONDecoder]]]) \
        -> Type[Deserializer]:
    """
    Converts a `JSONDecoder` class into an equivalent `Deserializer` class.
    :param decoder_cls: the decoder class type or a function that returns the type
    :return: the equivalent `Deserializer` class
    """
    name = decoder_cls.__name__ if isinstance(decoder_cls, type) else "%sLambdaTypeReturn" % id(decoder_cls)
    return type(
        "%sAsDeserializer" % name,
        (_JSONDecoderAsDeserializer,),
        {
            "decoder_type": property(lambda self: decoder_cls if isinstance(decoder_cls, type) else decoder_cls())
        }
    )
