from json import JSONDecoder, JSONEncoder
from typing import Callable, Any, Dict, Union, Iterable

from hgijson.json_converters._converters import json_decoder_to_deserializer, json_encoder_to_serializer
from hgijson.serialization import PropertyMapping


class JsonPropertyMapping(PropertyMapping):
    """
    Model of a mapping between a json property and a property of an object.
    """
    @property
    def json_property_getter(self) -> Callable[[Dict], Any]:
        return self.serialized_property_getter

    @json_property_getter.setter
    def json_property_getter(self, getter: Callable[[Dict], Any]):
        self.serialized_property_getter = getter

    @property
    def json_property_setter(self) -> Callable[[Any, Any], None]:
        return self.serialized_property_setter

    @json_property_setter.setter
    def json_property_setter(self, setter: Callable[[Any, Any], None]):
        self.serialized_property_setter = setter

    def __init__(
            self, json_property_name=None, object_property_name: str=None, object_constructor_parameter_name: str=None,
            *, object_constructor_argument_modifier: Callable[[Any], Any]=None,
            json_property_getter: Callable[[Dict], Any]=None, json_property_setter: Callable[[Any, Any], None]=None,
            object_property_getter: Callable[[Any], Any]=None, object_property_setter: Callable[[Any, Any], None]=None,
            encoder_cls: Union[type, Callable[[], type]]=JSONEncoder,
            decoder_cls: Union[type, Callable[[], type]]=JSONDecoder, 
            optional: bool=False,
            collection_factory: Callable[[Iterable], Any]=lambda items: list(items),
            collection_iter: Callable[[Any], Iterable]=lambda collection: iter(collection),
            parent_json_properties: Iterable[str]=None):
        """
        Constructor.
        :param json_property_name:
        :param object_property_name:
        :param object_constructor_parameter_name:
        :param object_constructor_argument_modifier:
        :param json_property_getter:
        :param json_property_setter:
        :param object_property_getter:
        :param object_property_setter:
        :param encoder_cls:
        :param decoder_cls:
        :param optional:
        """
        if json_property_name is not None:
            if json_property_getter is not None and json_property_setter is not None:
                raise ValueError("Redundant `json_property_name` argument given. It has been specified that a "
                                 "serialized property is to be used via the given property name and both a setter and "
                                 "getter of this property has been provided. To avoid confusion, the serialized "
                                 "property cannot be specified in this case.")

            if json_property_getter is None:
                def json_property_getter(obj_as_json: Dict):
                    if json_property_name not in obj_as_json:
                        if optional:
                            return None
                        else:
                            raise KeyError("No value for the non-optional key \"%s\" in the input JSON: %s"
                                             % (json_property_name, obj_as_json))
                    return obj_as_json[json_property_name]

            if json_property_setter is None:
                def json_property_setter(obj_as_json: Dict, value: Any):
                    obj_as_json[json_property_name] = value

        if parent_json_properties is not None:
            parent_json_properties = list(parent_json_properties)

            if json_property_getter is not None:
                top_level_json_property_getter = json_property_getter

                def json_property_getter(obj_as_json: Dict):
                    top_level_obj_as_json = obj_as_json
                    for ancestor in parent_json_properties:
                        obj_as_json = obj_as_json.get(ancestor, None)
                        if obj_as_json is None:
                            if optional:
                                return None
                            else:
                                raise KeyError("Parent keys missing \"%s\" in the input JSON: %s"
                                               % (".".join(parent_json_properties), top_level_obj_as_json))
                    return top_level_json_property_getter(obj_as_json)

            if json_property_setter is not None:
                top_level_json_property_setter = json_property_setter

                def json_property_setter(obj_as_json: Dict, value: Any):
                    for ancestor in parent_json_properties:
                        if ancestor not in obj_as_json:
                            obj_as_json[ancestor] = {}
                        obj_as_json = obj_as_json[ancestor]
                    top_level_json_property_setter(obj_as_json, value)

        if object_property_name is not None:
            if object_property_getter is not None and object_property_setter is not None:
                raise ValueError("Redundant `object_property_name` argument given. It has been specified that an "
                                 "object property is to be used via the given property name and both a setter and "
                                 "getter of this object property has been provided. To avoid confusion, the object "
                                 "property cannot be specified in this case.")

            if object_property_getter is None:
                def object_property_getter(obj: Any) -> Any:
                    return getattr(obj, object_property_name)

            if object_property_setter is None and object_constructor_parameter_name is None:
                def object_property_setter(obj: Any, value: Any):
                    if not hasattr(obj, object_property_name):
                        raise AttributeError("Object `%s` does not have the attribute `%s`"
                                             % (obj, object_property_name))
                    setattr(obj, object_property_name, value)

        encoder_as_serializer_cls = json_encoder_to_serializer(encoder_cls)
        decoder_as_serializer_cls = json_decoder_to_deserializer(decoder_cls)

        super().__init__(serialized_property_getter=json_property_getter,
                         serialized_property_setter=json_property_setter,
                         object_property_getter=object_property_getter,
                         object_property_setter=object_property_setter,
                         object_constructor_parameter_name=object_constructor_parameter_name,
                         object_constructor_argument_modifier=object_constructor_argument_modifier,
                         serializer_cls=encoder_as_serializer_cls, deserializer_cls=decoder_as_serializer_cls,
                         optional=optional,
                         collection_factory=collection_factory, collection_iter=collection_iter)
