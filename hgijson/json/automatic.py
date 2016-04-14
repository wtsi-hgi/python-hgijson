import copy
from abc import ABCMeta, abstractstaticmethod
from json import JSONEncoder
from typing import Dict, Optional, Iterable, Any, TypeVar

from hgijson.types import PrimitiveJsonSerializableType


class _RegisteredTypeJSONEncoder(JSONEncoder, metaclass=ABCMeta):
    """
    JSON encoder that will encode objects using the registered encoders. Works with in-built JSON library:
    ```
    import json

    register_json_encoder(MyObjectType, MyEncoderType)
    json.dumps(object_to_serialise, target_cls=_RegisteredTypeJSONEncoder)
    ```
    """
    @abstractstaticmethod
    def _get_json_encoders_for_type(type_to_encode: type) -> Optional[Iterable[JSONEncoder]]:
        """
        Gets the correct JSON encoder for the given type.
        :param type_to_encode: the type to encode
        :return: the encoder for the given type
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._encoder_cache = dict()    # type: Dict[type, JSONEncoder]

    def default(self, to_encode: Any) -> PrimitiveJsonSerializableType:
        type_to_encode = type(to_encode)

        encoder_type = self._get_json_encoders_for_type(type_to_encode)
        if encoder_type is None:
            # Unknown type: let standard JSON parser deal with it (will almost certainly raise an exception)
            encoder_type = JSONEncoder
        assert isinstance(encoder_type, type)

        if encoder_type not in self._encoder_cache:
            encoder = encoder_type(*self._args, **self._kwargs)
            self._encoder_cache[encoder_type] = encoder

        encoder = self._encoder_cache[encoder_type]
        assert isinstance(encoder, JSONEncoder)

        return encoder.default(to_encode)


RegisteredTypeJSONEncoderType = TypeVar("RegisteredTypeJSONEncoder", bound=_RegisteredTypeJSONEncoder)


class AutomaticJSONEncoderClassBuilder:
    """
    Builder for `JSONEncoder` class that is able to use a number of given `JSONEncoders` to automatically serialise
    models that may contain many models of different types.

    Similar to `jsonpublish` but without the global scope and able to be used with any json.dumps settings (unlike
    `jsonpublish` which (confusingly) can only be used by the settings that the developer made (see the package's
    __init__).
    """
    # Encoders for objects that are handled by the in-build JSON library
    _DEFAULT_JSON_ENCODERS = {
        dict: JSONEncoder,
        list: JSONEncoder,
        tuple: JSONEncoder,
        str: JSONEncoder,
        int: JSONEncoder,
        float: JSONEncoder,
        bool: JSONEncoder,
        type(None): JSONEncoder
    }

    def __init__(self):
        """
        Constructor.
        """
        self._json_encoders = dict()    # type: Dict[type, type]
        self.reset_registered_json_encoders()

    def get_json_encoders_for_type(self, type_to_encode: type) -> Optional[Iterable[JSONEncoder]]:
        """
        Gets the registered JSON encoder for the given type.
        :param type_to_encode: the type of object that is to be encoded
        :return: the encoder for the given object else `None` if unknown
        """
        if type_to_encode not in self._json_encoders:
            return None
        return self._json_encoders[type_to_encode]

    def register_json_encoder(self, encoder_type: type, encoder: JSONEncoder):
        """
        Register the given JSON encoder for use with the given object type.
        :param encoder_type: the type of object to encode
        :param encoder: the JSON encoder
        :return: this builder
        """
        self._json_encoders[encoder_type] = encoder
        return self

    def reset_registered_json_encoders(self):
        """
        Resets registered JSON encoders so that only ones supported by the in-built library are supported.
        """
        self._json_encoders = copy.copy(AutomaticJSONEncoderClassBuilder._DEFAULT_JSON_ENCODERS)

    def build(self) -> RegisteredTypeJSONEncoderType:
        """
        Builds JSON encoder that uses the encoders registered at the point in time when this method is called.
        :return: the JSON encoder
        """
        class_name = "%s_%s" % (_RegisteredTypeJSONEncoder.__class__.__name__, id(self))
        # Use encoders set at the point in time at which the encoder was built
        builder_snapshot = copy.deepcopy(self)
        return type(
                class_name,
                (_RegisteredTypeJSONEncoder, ),
                {
                    "_get_json_encoders_for_type": builder_snapshot.get_json_encoders_for_type
                }
        )
