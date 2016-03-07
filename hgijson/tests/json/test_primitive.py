import json
import unittest
from datetime import datetime
from datetime import timezone

from hgijson.json.primitive import StrJSONEncoder, FloatJSONDecoder, IntJSONDecoder, StrJSONDecoder, IntJSONEncoder, \
    FloatJSONEncoder, DatetimeISOFormatJSONEncoder, DatetimeISOFormatJSONDecoder


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


if __name__ == "__main__":
    unittest.main()
