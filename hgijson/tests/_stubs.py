from json import JSONEncoder

from hgicommon.models import Model
from hgijson.json_converters.automatic import _RegisteredTypeJSONEncoder


class StubModel(Model):
    """
    Stub `Model`.
    """


class StubRegisteredTypeJSONEncoder(_RegisteredTypeJSONEncoder):
    """
    Stub `_RegisteredTypeJSONEncoder`.
    """
    def _get_json_encoders_for_type(self) -> JSONEncoder:
        """ Unused - to satisfy the interface only. """
