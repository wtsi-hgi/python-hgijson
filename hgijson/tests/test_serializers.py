import unittest

from hgijson.serializers import PrimitiveSerializer, PrimitiveDeserializer


class TestPrimitiveSerializer(unittest.TestCase):
    """
    Tests for `PrimitiveSerializer`.
    """
    def test_serialize(self):
        serializer = PrimitiveSerializer()
        self.assertDictEqual(serializer.serialize({"a": 1}), {"a": 1})
        self.assertEqual(serializer.serialize([1, 2]), [1, 2])
        self.assertEqual(serializer.serialize((1, 2)), (1, 2))
        self.assertEqual(serializer.serialize("a"), "a")
        self.assertEqual(serializer.serialize(5), 5)
        self.assertEqual(serializer.serialize(5.5), 5.5)
        self.assertEqual(serializer.serialize(True), True)
        self.assertEqual(serializer.serialize(False), False)
        self.assertEqual(serializer.serialize(None), None)


class TestPrimitiveDeserializer(unittest.TestCase):
    """
    Tests for `PrimitiveDeserializer`.
    """
    def test_deserialize(self):
        deserializer = PrimitiveDeserializer()
        self.assertDictEqual(deserializer.deserialize({"a": 1}), {"a": 1})
        self.assertEqual(deserializer.deserialize([1, 2]), [1, 2])
        self.assertEqual(deserializer.deserialize((1, 2)), (1, 2))
        self.assertEqual(deserializer.deserialize("a"), "a")
        self.assertEqual(deserializer.deserialize(5), 5)
        self.assertEqual(deserializer.deserialize(5.5), 5.5)
        self.assertEqual(deserializer.deserialize(True), True)
        self.assertEqual(deserializer.deserialize(False), False)
        self.assertEqual(deserializer.deserialize(None), None)


if __name__ == "__main__":
    unittest.main()
