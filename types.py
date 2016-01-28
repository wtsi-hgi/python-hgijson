from typing import TypeVar, Dict, List, Tuple

SerializableType = TypeVar("Serializable")

PrimitiveUnionType = TypeVar("PrimitiveUnion")

PrimitiveJsonSerializableType = TypeVar("PrimitiveJsonSerializable", Dict, List, Tuple, str, int, float, bool, None)