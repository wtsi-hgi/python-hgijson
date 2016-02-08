from abc import abstractmethod, ABCMeta

from hgijson.types import SerializableType


class DictJSONDecoder(metaclass=ABCMeta):
    """
    Decoder of JSON represented as a Python dictionary.
    """
    @abstractmethod
    def decode_dict(self, json_as_dict: dict) -> SerializableType:
        """
        Decodes the given JSON, represented as a Python dictionary.
        :param json_as_dict: the JSON represented in a dictionary
        :return: the decoded object
        """
        pass
