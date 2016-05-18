import json
import unittest
from datetime import datetime, timezone

from hgijson.json.primitive import StrJSONDecoder, IntJSONEncoder, FloatJSONEncoder, FloatJSONDecoder, \
    DatetimeEpochJSONEncoder, DatetimeEpochJSONDecoder, DatetimeISOFormatJSONDecoder, DatetimeISOFormatJSONEncoder, \
    IntJSONDecoder
from hgijson.json.primitive import StrJSONEncoder
from hgijson.tests.json._mocks import MockSetJSONEncoder, MockSetJSONDecoder


class TestStrJSONEncoder(unittest.TestCase):
    """
    Tests for `StrJSONEncoder`.
    """
    def test_default_with_str(self):
        self.assertEqual(StrJSONEncoder().default("123"), "123")

    def test_default_with_int(self):
        self.assertEqual(StrJSONEncoder().default(123), "123")

    def test_default_with_float(self):
        self.assertEqual(StrJSONEncoder().default(12.3), "12.3")


class TestStrJSONDecoder(unittest.TestCase):
    """
    Tests for `TestStrJSONDecoder`.
    """
    def test_decode_with_string(self):
        self.assertEqual(StrJSONDecoder().decode("123"), "123")

    def test_with_json_loads(self):
        self.assertEqual(json.loads("123", cls=StrJSONDecoder), "123")


class TestIntJSONEncoder(unittest.TestCase):
    """
    Tests for `IntJSONEncoder`.
    """
    def test_default_with_str(self):
        self.assertEqual(IntJSONEncoder().default("123"), 123)

    def test_default_with_int(self):
        self.assertEqual(IntJSONEncoder().default(123), 123)

    def test_default_with_float(self):
        self.assertEqual(IntJSONEncoder().default(12.3), 12)


class TestIntJSONDecoder(unittest.TestCase):
    """
    Tests for `IntJSONDecoder`.
    """
    def test_decode_with_int_as_string(self):
        self.assertEqual(IntJSONDecoder().decode("123"), 123)

    def test_with_json_loads_and_int_as_string(self):
        self.assertEqual(json.loads("123", cls=IntJSONDecoder), 123)


class TestFloatJSONEncoder(unittest.TestCase):
    """
    Tests for `FloatJSONEncoder`.
    """
    def test_default_with_str(self):
        self.assertEqual(FloatJSONEncoder().default("12.3"), 12.3)

    def test_default_with_int(self):
        self.assertEqual(FloatJSONEncoder().default(123), 123.0)

    def test_default_with_float(self):
        self.assertEqual(FloatJSONEncoder().default(12.3), 12.3)


class TestFloatJSONDecoder(unittest.TestCase):
    """
    Tests for `FloatJSONDecoder`.
    """
    def test_decode_with_float_as_string(self):
        self.assertEqual(FloatJSONDecoder().decode("12.3"), 12.3)

    def test_with_json_loads_and_int_as_string(self):
        self.assertEqual(json.loads("12.3", cls=FloatJSONDecoder), 12.3)


class TestDatetimeEpochJSONEncoder(unittest.TestCase):
    """
    Tests for `DatetimeEpochJSONEncoder`.
    """
    def test_default(self):
        value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(DatetimeEpochJSONEncoder().default(value), 0)


class TestDatetimeEpochJSONDecoder(unittest.TestCase):
    """
    Tests for `DatetimeEpochJSONDecoder`.
    """
    def test_decode(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(DatetimeEpochJSONDecoder().decode("0"), expected_value)

    def test_with_json_loads(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(json.loads("0", cls=DatetimeEpochJSONDecoder), expected_value)


class TestDatetimeISOFormatJSONEncoder(unittest.TestCase):
    """
    Tests for `DatetimeISOFormatJSONEncoder`.
    """
    def test_default(self):
        value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(DatetimeISOFormatJSONEncoder().default(value), "1970-01-01T00:00:00+00:00")


class TestDatetimeISOFormatJSONDecoder(unittest.TestCase):
    """
    Tests for `DatetimeISOFormatJSONDecoder`.
    """
    def test_decode_with_numerical_offset(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(DatetimeISOFormatJSONDecoder().decode("1970-01-01T00:00:00+00:00"), expected_value)

    def test_decode_with_special_representation_offset(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(DatetimeISOFormatJSONDecoder().decode("1970-01-01T00:00:00Z"), expected_value)

    def test_with_json_loads(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(json.loads("1970-01-01T00:00:00+00:00", cls=DatetimeISOFormatJSONDecoder), expected_value)


class TestSetJSONEncoder(unittest.TestCase):
    """
    Tests for `SetJSONEncoder`.
    """
    def setUp(self):
        self.item_encoder_cls = IntJSONEncoder
        self.encoder = MockSetJSONEncoder(self.item_encoder_cls)
        self.values = {1, 5, 7, 9}

    def test_default(self):
        self.assertEqual(self.encoder.encode(self.values), json.dumps(list(self.values)))

    def test_default_with_unsupported_type(self):
        self.assertRaises(TypeError, self.encoder.encode, object())


class TestSetJSONDecoder(unittest.TestCase):
    """
    Tests for `SetJSONDecoder`.
    """
    def setUp(self):
        self.item_decoder_cls = IntJSONDecoder
        self.decoder = MockSetJSONDecoder(self.item_decoder_cls)
        self.values = {1, 5, 7, 9}

    def test_decode(self):
        values_as_json_string = json.dumps(list(self.values))
        self.assertEqual(self.decoder.decode(values_as_json_string), self.values)


if __name__ == "__main__":
    unittest.main()
