from json import JSONDecoder, JSONEncoder

from typing import Any

from datetime import datetime
from time import mktime


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
        return str(to_decode)


class DatetimeEpochJSONEncoder(JSONEncoder):
    """
    JSON encoder for datetime
    """
    def default(self, to_encode: datetime) -> int:
        return int(mktime(to_encode.timetuple()))


class DatetimeEpochJSONDecoder(JSONDecoder):
    """
    JSON decoder for datetime
    """
    def decode(self, to_decode: str, **kwargs) -> datetime:
        return datetime.fromtimestamp(int(to_decode))
