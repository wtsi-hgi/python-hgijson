from json import JSONDecoder, JSONEncoder
from typing import Tuple, Dict, Union, List

from hgicommon.models import Model


DefaultSupportedJSONSerializableType = Union[
    Dict, List, Tuple, str, int, float, bool, None
]


class JsonPropertyMapping(Model):
    """
    Model of a mapping between a json property and a property of an object.
    """
    def __init__(
            self, json_property: str, object_property: str, constructor_parameter: str=None,
            encoder: type=JSONEncoder, decoder: type=JSONDecoder):
        self.json_property = json_property
        self.object_property = object_property
        self.constructor_parameter = constructor_parameter
        self.encoder = encoder
        self.decoder = decoder
