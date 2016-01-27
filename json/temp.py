from typing import Dict, Tuple
from typing import TypeVar, List

PrimitiveJsonSerializableType = TypeVar("PrimitiveJsonSerializable", Dict, List, Tuple, str, int, float, bool, None)
