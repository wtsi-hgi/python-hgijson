import unittest

from hgijson.json.models import JsonPropertyMapping


class TestPropertyMapping(unittest.TestCase):
    """
    Tests for `JsonPropertyMapping`.
    """
    def test_init_with_serialized_property_name_and_getter_and_setter(self):
        self.assertRaises(ValueError, JsonPropertyMapping, json_property_name="a",
                          json_property_getter=lambda: None, json_property_setter=lambda: None)

    def test_init_with_object_and_serialized_names(self):
        property_mapping = JsonPropertyMapping("serialized_a", "a", "constructor_a")
        self.assertIsNotNone(property_mapping.object_property_getter)
        self.assertIsNone(property_mapping.object_property_setter)
        self.assertIsNotNone(property_mapping.serialized_property_getter)
        self.assertIsNotNone(property_mapping.serialized_property_setter)
        self.assertIsNotNone(property_mapping.object_constructor_parameter_name)

    def test_json_property_getter_property(self):
        property_mapping = JsonPropertyMapping("a")
        getter = lambda: None
        property_mapping.json_property_getter = getter
        self.assertEqual(property_mapping.json_property_getter, getter)

    def test_json_property_setter_property(self):
        property_mapping = JsonPropertyMapping("a")
        setter = lambda: None
        property_mapping.json_property_setter = setter
        self.assertEqual(property_mapping.json_property_setter, setter)


if __name__ == "__main__":
    unittest.main()
