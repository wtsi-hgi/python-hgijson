from json import JSONEncoder

from hgijson.json_converters.automatic import _RegisteredTypeJSONEncoder
from hgijson.tests._models import BaseModel


class StubModel(BaseModel):
    """
    Stub `Model`.
    """


class StubRegisteredTypeJSONEncoder(_RegisteredTypeJSONEncoder):
    """
    Stub `_RegisteredTypeJSONEncoder`.
    """
    def _get_json_encoders_for_type(self) -> JSONEncoder:
        """ Unused - to satisfy the interface only. """
