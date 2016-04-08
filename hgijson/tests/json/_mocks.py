from hgijson.json.primitive import SetJSONEncoder, SetJSONDecoder


class MockSetJSONEncoder(SetJSONEncoder):
    """
    Mock implementation of `SetJSONEncoder`.
    """
    def __init__(self, item_encoder_cls: type, *args, **kwargs):
        self._injected_item_encoder_cls = item_encoder_cls
        super().__init__(*args, **kwargs)

    @property
    def item_encoder_cls(self) -> type:
        return self._injected_item_encoder_cls


class MockSetJSONDecoder(SetJSONDecoder):
    """
    Mock implementation of `SetJSONDecoder`.
    """
    def __init__(self, item_decoder_cls: type, *args, **kwargs):
        self._injected_item_decoder_cls = item_decoder_cls
        super().__init__(*args, **kwargs)

    @property
    def item_decoder_cls(self) -> type:
        return self._injected_item_decoder_cls
