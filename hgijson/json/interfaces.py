from abc import abstractmethod, ABCMeta

from hgijson.types import SerializableType, PrimitiveJsonSerializableType


class ParsedJSONDecoder(metaclass=ABCMeta):
    """
    Decoder of JSON parsed from a string into primitive Python objects.
    """
    @abstractmethod
    def decode_parsed(self, parsed_json: PrimitiveJsonSerializableType) -> SerializableType:
        """
        Decodes the given JSON, represented as primitive Python objects.
        :param parsed_json: the JSON
        :return: the decoded object
        """
