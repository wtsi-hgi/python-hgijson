import json
from abc import ABCMeta, abstractproperty
from datetime import datetime, timezone
from json import JSONDecoder, JSONEncoder
from typing import Any, Set, TypeVar, Generic

from dateutil.parser import parser

from hgijson.json.interfaces import ParsedJSONDecoder
from hgijson.types import PrimitiveJsonSerializableType, SerializableType

ItemType = TypeVar("ItemType")


class StrJSONEncoder(JSONEncoder):
    """
    JSON encoder from any type that implements `__str__` to its string representation.
    """
    def default(self, to_encode: Any) -> str:
        return str(to_encode)


class StrJSONDecoder(JSONDecoder):
    """
    JSON decoder for strings.
    """
    def decode(self, to_decode: str, **kwargs) -> str:
        return str(to_decode)


class IntJSONEncoder(JSONEncoder):
    """
    JSON encoder from any type that implements `__int__`  to an integer.
    """
    def default(self, to_encode: Any) -> str:
        return int(to_encode)


class IntJSONDecoder(JSONDecoder):
    """
    JSON decoder for integers.
    """
    def decode(self, to_decode: str, **kwargs) -> int:
        return int(to_decode)


class FloatJSONEncoder(JSONEncoder):
    """
    JSON encoder from any type that implements `__float__`  to a float.
    """
    def default(self, to_encode: Any) -> str:
        return float(to_encode)


class FloatJSONDecoder(JSONDecoder):
    """
    JSON decoder for floats.
    """
    def decode(self, to_decode: str, **kwargs) -> str:
        return float(to_decode)


class DatetimeISOFormatJSONEncoder(JSONEncoder):
    """
    JSON encoder for datetime to ISO 8601 format.
    """
    def default(self, to_encode: datetime) -> str:
        return to_encode.isoformat()


class DatetimeISOFormatJSONDecoder(JSONDecoder):
    """
    JSON decoder for datetime as ISO 8601 formatted string.
    """
    _DATE_PARSER = parser()

    def decode(self, to_decode: str, **kwargs) -> datetime:
        return DatetimeISOFormatJSONDecoder._DATE_PARSER.parse(to_decode)


class DatetimeEpochJSONEncoder(JSONEncoder):
    """
    JSON encoder for datetime to seconds since the epoch (1970-01-01). If the datetime has microsecond precision, it
    will be rounded to the nearest corresponding second since the epoch.
    """
    def default(self, to_encode: datetime) -> int:
        return int(to_encode.timestamp())


class DatetimeEpochJSONDecoder(JSONDecoder):
    """
    JSON decoder for datetime as seconds since the epoch (1970-01-01).
    """
    def decode(self, to_decode: str, **kwargs) -> datetime:
        return datetime.fromtimestamp(int(to_decode), timezone.utc)


class SetJSONEncoder(Generic[ItemType], JSONEncoder, metaclass=ABCMeta):
    """
    Encoder for sets, which serialises sets into JSON lists.
    """
    @abstractproperty
    def item_encoder_cls(self) -> type:
        """
        The type of JSON encoder to use for each item in a set.
        :return: the type of item JSON encoder - must be a subclass of `JSONEncoder`
        """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item_encoder = self.item_encoder_cls(*args, **kwargs)     # type: JSONEncoder

    def default(self, to_encode: Set[ItemType]) -> PrimitiveJsonSerializableType:
        if not isinstance(to_encode, Set):
            super().default(to_encode)
        encoded_set = []
        for item in to_encode:
            encoded_item = self._item_encoder.default(item)
            encoded_set.append(encoded_item)
        return encoded_set


class SetJSONDecoder(Generic[ItemType], JSONDecoder, ParsedJSONDecoder, metaclass=ABCMeta):
    """
    Decoder for sets, which deserialises JSON lists into Python sets.
    """
    @abstractproperty
    def item_decoder_cls(self) -> type:
        """
        The type of JSON decoder for each item in a set that has been encoded as a JSON list.
        :return: the type of item JSON decoder - must be a subclass of `JSONDecoder`
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._item_decoder = self.item_decoder_cls(*args, **kwargs)     # type: JSONDecoder

    def decode(self, to_decode: str, **kwargs) -> Set[ItemType]:
        to_decode_as_list = json.loads(to_decode)
        return self.decode_parsed(to_decode_as_list)

    def decode_parsed(self, parsed_json: PrimitiveJsonSerializableType) -> SerializableType:
        decoded_set = set()
        for item in parsed_json:
            if isinstance(self._item_decoder, ParsedJSONDecoder):
                # Optimisation: `ParsedJSONDecoder` knows how to decode a dict - no need to convert to JSON as string
                decoded_item = self._item_decoder.decode_parsed(item)
            else:
                item_as_string = json.dumps(item)
                decoded_item = self._item_decoder.decode(item_as_string)

            decoded_set.add(decoded_item)
        return decoded_set
