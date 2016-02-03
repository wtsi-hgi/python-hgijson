from json import JSONDecoder, JSONEncoder

from typing import Any


class StrJSONEncoder(JSONEncoder):
    """
    JSON encoder from any type to its string representation.
    """
    def default(self, to_encode: Any) -> str:
        return str(to_encode)


class IntJSONDecoder(JSONDecoder):
    """
    JSON decoder for integers.
    """
    def decode(self, to_decode: str, **kwargs) -> int:
        return int(to_decode)


class FloatJSONDecoder(JSONDecoder):
    """
    JSON decoder for floats.
    """
    def decode(self, to_decode: str, **kwargs) -> float:
        return float(to_decode)


class StrJSONDecoder(JSONDecoder):
    """
    JSON decoder for strings.
    """
    def decode(self, to_decode: str, **kwargs) -> str:
        return str(to_decode)
