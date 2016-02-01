import json
import unittest
from json import JSONEncoder

from hgijson.json.automatic import AutomaticJSONEncoderClassBuilder
from hgijson.tests._stubs import StubModel, StubRegisteredTypeJSONEncoder


class TestRegisteredTypeJSONEncoder(unittest.TestCase):
    """
    Tests for `_RegisteredTypeJSONEncoder`.
    """
    def test_default_when_unknown(self):
        self.assertRaises(TypeError, json.dumps, StubModel(), cls=StubRegisteredTypeJSONEncoder)

    def test_default_when_standard_type(self):
        dict = {1: 2, 3: []}
        self.assertEqual(json.dumps(dict, cls=StubRegisteredTypeJSONEncoder), json.dumps(dict))


class TestAutomaticJSONEncoderClassBuilder(unittest.TestCase):
    """
    Tests for `AutomaticJSONEncoderClassBuilder`.
    """
    def setUp(self):
        self.encoder_builder = AutomaticJSONEncoderClassBuilder()

    def test_get_json_encoders_for_type_if_not_known(self):
        self.assertIsNone(self.encoder_builder.get_json_encoders_for_type(JSONEncoder))

    def test_get_json_encoders_for_type_has_encoders_for_standard_types(self):
        repeat_to_test_reset = True
        types_to_check = [dict, list, tuple, str, int, float, bool, type(None)]
        while repeat_to_test_reset:
            for type_to_check in types_to_check:
                self.assertTrue(issubclass(self.encoder_builder.get_json_encoders_for_type(type_to_check), JSONEncoder))
            self.encoder_builder.reset_registered_json_encoders()
            repeat_to_test_reset = False

    def test_get_json_encoders_for_type_if_registered(self):
        self.encoder_builder.register_json_encoder(JSONEncoder, JSONEncoder)
        self.assertEqual(self.encoder_builder.get_json_encoders_for_type(JSONEncoder), JSONEncoder)

    def test_reset_registered_json_encoders(self):
        self.encoder_builder.register_json_encoder(JSONEncoder, JSONEncoder)
        self.encoder_builder.reset_registered_json_encoders()
        self.assertIsNone(self.encoder_builder.get_json_encoders_for_type(JSONEncoder))

    def test_build_with_no_registered_encoders(self):
        Encoder = self.encoder_builder.build()
        self.assertTrue(issubclass(Encoder, JSONEncoder))
        # Should work with types supported by default
        test_object = {1: 2}
        self.assertEqual(json.dumps(test_object, cls=Encoder), json.dumps(test_object))
        self.assertRaises(TypeError, json.dumps, StubModel(), cls=Encoder)

    def test_build_with_registered_encoders(self):
        # Sanity check
        self.assertRaises(TypeError, json.dumps, StubModel(), cls=self.encoder_builder.build())

        expect_encode = "expected encoding"

        class StubModelJSONEncoder(JSONEncoder):
            def default(self, o):
                assert isinstance(o, StubModel)
                return expect_encode
        self.encoder_builder.register_json_encoder(StubModel, StubModelJSONEncoder)

        self.assertEqual(json.dumps(StubModel(), cls=self.encoder_builder.build()), json.dumps(expect_encode))

    def test_build_not_influenced_by_future_registrations(self):
        Encoder = self.encoder_builder.build()

        expect_encode = "expected encoding"

        class StubModelJSONEncoder(JSONEncoder):
            def default(self, o):
                assert isinstance(o, StubModel)
                return expect_encode
        self.encoder_builder.register_json_encoder(StubModel, StubModelJSONEncoder)

        self.assertRaises(TypeError, json.dumps, StubModel(), cls=Encoder)
        self.assertEqual(json.dumps(StubModel(), cls=self.encoder_builder.build()), json.dumps(expect_encode))


if __name__ == "__main__":
    unittest.main()
