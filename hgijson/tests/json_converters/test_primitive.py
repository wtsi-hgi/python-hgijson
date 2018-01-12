import json
import unittest
from datetime import datetime, timezone

from hgijson.json_converters.primitive import StrJSONDecoder, IntJSONEncoder, FloatJSONEncoder, FloatJSONDecoder, \
    DatetimeEpochJSONEncoder, DatetimeEpochJSONDecoder, DatetimeISOFormatJSONDecoder, DatetimeISOFormatJSONEncoder, \
    IntJSONDecoder
from hgijson.json_converters.primitive import StrJSONEncoder


class TestStrJSONEncoder(unittest.TestCase):
    """
    Tests for `StrJSONEncoder`.
    """
    def test_default_with_str(self):
        self.assertEqual("123", StrJSONEncoder().default("123"))

    def test_default_with_int(self):
        self.assertEqual("123", StrJSONEncoder().default(123))

    def test_default_with_float(self):
        self.assertEqual("12.3", StrJSONEncoder().default(12.3))


class TestStrJSONDecoder(unittest.TestCase):
    """
    Tests for `TestStrJSONDecoder`.
    """
    def test_decode_with_string(self):
        self.assertEqual("123", StrJSONDecoder().decode("123"))

    def test_with_json_loads(self):
        self.assertEqual("123", json.loads("123", cls=StrJSONDecoder))


class TestIntJSONEncoder(unittest.TestCase):
    """
    Tests for `IntJSONEncoder`.
    """
    def test_default_with_str(self):
        self.assertEqual(123, IntJSONEncoder().default("123"))

    def test_default_with_int(self):
        self.assertEqual(123, IntJSONEncoder().default(123))

    def test_default_with_float(self):
        self.assertEqual(12, IntJSONEncoder().default(12.3))


class TestIntJSONDecoder(unittest.TestCase):
    """
    Tests for `IntJSONDecoder`.
    """
    def test_decode_with_int_as_string(self):
        self.assertEqual(123, IntJSONDecoder().decode("123"))

    def test_with_json_loads_and_int_as_string(self):
        self.assertEqual(123, json.loads("123", cls=IntJSONDecoder))


class TestFloatJSONEncoder(unittest.TestCase):
    """
    Tests for `FloatJSONEncoder`.
    """
    def test_default_with_str(self):
        self.assertEqual(12.3, FloatJSONEncoder().default("12.3"))

    def test_default_with_int(self):
        self.assertEqual(123.0, FloatJSONEncoder().default(123))

    def test_default_with_float(self):
        self.assertEqual(12.3, FloatJSONEncoder().default(12.3))


class TestFloatJSONDecoder(unittest.TestCase):
    """
    Tests for `FloatJSONDecoder`.
    """
    def test_decode_with_float_as_string(self):
        self.assertEqual(12.3, FloatJSONDecoder().decode("12.3"))

    def test_with_json_loads_and_int_as_string(self):
        self.assertEqual(12.3, json.loads("12.3", cls=FloatJSONDecoder))


class TestDatetimeEpochJSONEncoder(unittest.TestCase):
    """
    Tests for `DatetimeEpochJSONEncoder`.
    """
    def test_default(self):
        value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(0, DatetimeEpochJSONEncoder().default(value))


class TestDatetimeEpochJSONDecoder(unittest.TestCase):
    """
    Tests for `DatetimeEpochJSONDecoder`.
    """
    def test_decode(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(expected_value, DatetimeEpochJSONDecoder().decode("0"))

    def test_with_json_loads(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(expected_value, json.loads("0", cls=DatetimeEpochJSONDecoder))


class TestDatetimeISOFormatJSONEncoder(unittest.TestCase):
    """
    Tests for `DatetimeISOFormatJSONEncoder`.
    """
    def test_default(self):
        value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual("1970-01-01T00:00:00+00:00", DatetimeISOFormatJSONEncoder().default(value))


class TestDatetimeISOFormatJSONDecoder(unittest.TestCase):
    """
    Tests for `DatetimeISOFormatJSONDecoder`.
    """
    def test_decode_with_numerical_offset(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(expected_value, DatetimeISOFormatJSONDecoder().decode_parsed("1970-01-01T00:00:00+00:00"))

    def test_decode_with_special_representation_offset(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(expected_value, DatetimeISOFormatJSONDecoder().decode_parsed("1970-01-01T00:00:00Z"))

    def test_with_json_loads(self):
        expected_value = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(expected_value, json.loads('"1970-01-01T00:00:00+00:00"', cls=DatetimeISOFormatJSONDecoder))


if __name__ == "__main__":
    unittest.main()
