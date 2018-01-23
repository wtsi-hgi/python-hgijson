import unittest
from typing import Iterable, TypeVar, Generic, List, Set

from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from hgijson.tests._models import BaseModel

_JSON_CUSTOM_COLLECTION_PROPERTY = "json-custom-collection"
_JSON_SET_COLLECTION_PROPERTY = "json-set-collection"

_CollectionItemType = TypeVar("CollectionItemType")


class _CustomCollection(Generic[_CollectionItemType], BaseModel):
    def __init__(self, items: Iterable[_CollectionItemType]=None):
        self._items = set(items) if items is not None else set()

    def add(self, item: _CollectionItemType):
        self._items.add(item)

    def get_iterator(self):
        return iter(self._items)


class _Container(BaseModel):
    @property
    def set_collection(self):
        return self._set_collection

    def __init__(self, set_collection: Set, custom_collection_items: List[int]=None):
        self.custom_collection = _CustomCollection[int](custom_collection_items)
        self._set_collection = set_collection


_container_mappings = [
    JsonPropertyMapping(_JSON_CUSTOM_COLLECTION_PROPERTY, "custom_collection", collection_factory=_CustomCollection,
                        collection_iter=lambda collection: collection.get_iterator()),
    JsonPropertyMapping(
        _JSON_SET_COLLECTION_PROPERTY, object_property_getter=lambda container: container.set_collection,
        object_constructor_parameter_name="set_collection", collection_factory=set),
]
_ContainerJSONEncoder = MappingJSONEncoderClassBuilder(_Container, _container_mappings).build()
_ContainerJSONDecoder = MappingJSONDecoderClassBuilder(_Container, _container_mappings).build()


class TestCollectionSupport(unittest.TestCase):
    """
    Testing for collection support.
    """
    def setUp(self):
        self.model = _Container({1, 2, 3}, [4, 5, 6])
        self.model_as_json = {
            _JSON_CUSTOM_COLLECTION_PROPERTY: list(self.model.custom_collection.get_iterator()),
            _JSON_SET_COLLECTION_PROPERTY: list(self.model.set_collection)
        }

    def test_encode(self):
        model_as_json = _ContainerJSONEncoder().default(self.model)
        self.assertEqual(self.model_as_json, model_as_json)

    def test_decode(self):
        model = _ContainerJSONDecoder().decode_parsed(self.model_as_json)
        self.assertEqual(self.model, model)


if __name__ == "__main__":
    unittest.main()
