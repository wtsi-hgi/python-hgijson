from abc import abstractmethod, ABCMeta
from json import JSONDecoder

from hgijson.custom_types import SerializableType, PrimitiveJsonType


class ParsedJSONDecoder(JSONDecoder, metaclass=ABCMeta):
    """
    Decoder of JSON parsed from a string into primitive Python objects.
    """
    @abstractmethod
    def decode_parsed(self, parsed_json: PrimitiveJsonType) -> SerializableType:
        """
        Decodes the given JSON, represented as primitive Python objects.
        :param parsed_json: the JSON
        :return: the decoded object
        """
