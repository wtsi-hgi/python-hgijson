from json import JSONEncoder

from hgicommon.collections import Metadata
from hgicommon.serialization.types import PrimitiveJsonSerializableType


class MetadataJSONEncoder(JSONEncoder):
    """
    JSON encoder for `Metadata` instances.

    Do not use as target_cls in `json.dumps` if the metadata collection being serialised contains values with types that cannot
    be converted to JSON by default. In such cases, this class can be used in `AutomaticJSONEncoderClassBuilder` along
    with encoders that handle other unsupported types or it should be used within another decoder.
    """
    def default(self, to_encode: Metadata) -> PrimitiveJsonSerializableType:
        if not isinstance(to_encode, Metadata):
            JSONEncoder.default(self, to_encode)

        return to_encode._data
