from typing import TypeVar, Dict, List, Tuple, Union

SerializableType = TypeVar("Serializable")

# TODO: Why is this needed?
PrimitiveUnionType = TypeVar("PrimitiveUnion")

PrimitiveJsonType = Union[Dict, List, Tuple, str, int, float, bool, None]
