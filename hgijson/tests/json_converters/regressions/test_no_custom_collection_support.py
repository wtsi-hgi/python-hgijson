import unittest
from typing import Iterable, TypeVar, Generic

from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from hgijson.tests._models import BaseModel

_JSON_COLLECTION_PROPERTY = "json-collection"

_CollectionItemType = TypeVar("CollectionItemType")


class _CustomCollection(Generic[_CollectionItemType], BaseModel):
    def __init__(self, items: Iterable[_CollectionItemType]=None):
        self._items = set(items) if items is not None else set()

    def add(self, item: _CollectionItemType):
        self._items.add(item)

    def get_iterator(self):
        return iter(self._items)


class _Container(BaseModel):
    def __init__(self):
        self.collection = _CustomCollection[int]([1, 2, 3])


_container_mappings = [
    JsonPropertyMapping(_JSON_COLLECTION_PROPERTY, "collection", collection_factory=_CustomCollection,
                        collection_iter=lambda collection: collection.get_iterator())
]
_ContainerJSONEncoder = MappingJSONEncoderClassBuilder(_Container, _container_mappings).build()
_ContainerJSONDecoder = MappingJSONDecoderClassBuilder(_Container, _container_mappings).build()


class TestNoCustomCollectionSupportRegression(unittest.TestCase):
    """
    Testing for collection support.
    """
    def setUp(self):
        self.model = _Container()
        self.model_as_json = {_JSON_COLLECTION_PROPERTY: list(self.model.collection.get_iterator())}

    def test_encode(self):
        model_as_json = _ContainerJSONEncoder().default(self.model)
        self.assertEqual(self.model_as_json, model_as_json)

    def test_decode(self):
        model = _ContainerJSONDecoder().decode_parsed(self.model_as_json)
        self.assertEqual(self.model, model)


if __name__ == "__main__":
    unittest.main()
