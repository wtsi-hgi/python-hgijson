from json import JSONEncoder, JSONDecoder

from hgijson.json.primitive import SetJSONEncoder, SetJSONDecoder


class MockSetJSONEncoder(SetJSONEncoder):
    """
    Mock implementation of `SetJSONEncoder`.
    """
    def __init__(self, item_encoder: JSONEncoder):
        super().__init__()
        self._item_encoder = item_encoder

    @property
    def item_encoder(self) -> JSONEncoder:
        return self._item_encoder


class MockSetJSONDecoder(SetJSONDecoder):
    """
    Mock implementation of `SetJSONDecoder`.
    """
    def __init__(self, item_decoder: JSONDecoder):
        super().__init__()
        self._item_decoder = item_decoder

    @property
    def item_decoder(self) -> JSONDecoder:
        return self._item_decoder
