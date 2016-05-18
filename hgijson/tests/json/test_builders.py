import json
import unittest
from json import JSONDecoder, JSONEncoder

from hgicommon.models import Model

from hgijson.json._serialization import MappingJSONDecoder
from hgijson.json._serialization import MappingJSONEncoder
from hgijson.json.builders import MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder, \
    SetJSONEncoderClassBuilder, SetJSONDecoderClassBuilder
from hgijson.json.models import JsonPropertyMapping
from hgijson.tests._models import SimpleModel, ComplexModel
from hgijson.tests.json._helpers import create_complex_model_with_json_representation,\
    create_simple_model_with_json_representation
from hgijson.tests.json._serializers import get_simple_model_json_property_mappings, \
    get_complex_model_json_property_mappings


class _Named(Model):
    def __init__(self):
        super().__init__()
        self.name = None    # type: str


class _Identifiable(Model):
    def __init__(self):
        super().__init__()
        self.id = None    # type: int


class _Employee(_Named, _Identifiable, Model):
    def __init__(self):
        super().__init__()
        self.title = None


class TestMappingJSONEncoderClassBuilder(unittest.TestCase):
    """
    Tests for `MappingJSONEncoderClassBuilder`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]
        self.complex_model = create_complex_model_with_json_representation()[0]
        self.complex_model_as_json = create_complex_model_with_json_representation()[1]

    def test_build(self):
        encoder_builder = MappingJSONEncoderClassBuilder()
        encoder_builder.target_cls = SimpleModel
        encoder_builder.mappings = get_simple_model_json_property_mappings()

        encoder_cls = encoder_builder.build()
        encoder = encoder_cls()     # type: MappingJSONEncoder

        encoded = encoder.default(self.simple_model)
        self.assertDictEqual(encoded, self.simple_model_as_json)

    def test_build_with_superclass(self):
        SimpleModelJSONEncoder = MappingJSONEncoderClassBuilder(
            SimpleModel, get_simple_model_json_property_mappings()).build()

        encoder_builder = MappingJSONEncoderClassBuilder()
        encoder_builder.target_cls = ComplexModel
        encoder_builder.mappings = get_complex_model_json_property_mappings()
        encoder_builder.superclasses = (SimpleModelJSONEncoder, )

        encoder_cls = encoder_builder.build()
        encoder = encoder_cls()     # type: MappingJSONEncoder

        encoded = encoder.default(self.complex_model)
        self.assertDictEqual(encoded, self.complex_model_as_json)

    def test_build_with_multiple_superclasses(self):
        NamedJSONEncoder = MappingJSONEncoderClassBuilder(_Named, [
            JsonPropertyMapping("name", "name")
        ]).build()
        IdentifiableJSONEncoder = MappingJSONEncoderClassBuilder(_Named, [
            JsonPropertyMapping("id", "id")
        ]).build()
        EmployeeJSONEncoder = MappingJSONEncoderClassBuilder(_Employee, [
           JsonPropertyMapping("title", "title"),
        ], (NamedJSONEncoder, IdentifiableJSONEncoder)).build()

        employee = _Employee()
        employee.name = "Bob"
        employee.id = 42
        employee.title = "Software Dev"
        employee_as_json = {
            "name": employee.name,
            "id": employee.id,
            "title": employee.title
        }
        self.assertEqual(EmployeeJSONEncoder().default([employee]), [employee_as_json])


class TestMappingJSONDecoderClassBuilder(unittest.TestCase):
    """
    Tests for `MappingJSONDecoderClassBuilder`.
    """
    def setUp(self):
        self.simple_model = create_simple_model_with_json_representation()[0]
        self.simple_model_as_json = create_simple_model_with_json_representation()[1]
        self.complex_model = create_complex_model_with_json_representation()[0]
        self.complex_model_as_json = create_complex_model_with_json_representation()[1]

    def test_build(self):
        decoder_builder = MappingJSONDecoderClassBuilder()
        decoder_builder.target_cls = SimpleModel
        decoder_builder.mappings = get_simple_model_json_property_mappings()

        decoder_cls = decoder_builder.build()
        decoder = decoder_cls()     # type: MappingJSONDecoder

        decoded = decoder.decode(json.dumps(self.simple_model_as_json))
        self.assertEqual(decoded, self.simple_model)

    def test_build_with_superclass(self):
        SimpleModelJSONDecoder = MappingJSONDecoderClassBuilder(
            target_cls=SimpleModel, mappings=get_simple_model_json_property_mappings()).build()

        decoder_builder = MappingJSONDecoderClassBuilder()
        decoder_builder.superclasses = (SimpleModelJSONDecoder, )
        decoder_builder.target_cls = ComplexModel
        decoder_builder.mappings = get_complex_model_json_property_mappings()

        decoder_cls = decoder_builder.build()
        decoder = decoder_cls()     # type: MappingJSONDecoder

        decoded = decoder.decode(json.dumps(self.complex_model_as_json))
        self.assertEqual(decoded, self.complex_model)

    def test_build_with_multiple_superclasses(self):
        NamedJSONDecoder = MappingJSONDecoderClassBuilder(_Named, [
            JsonPropertyMapping("name", "name")
        ]).build()
        IdentifiableJSONDecoder = MappingJSONDecoderClassBuilder(_Named, [
            JsonPropertyMapping("id", "id")
        ]).build()
        EmployeeJSONDecoder = MappingJSONDecoderClassBuilder(_Employee, [
           JsonPropertyMapping("title", "title"),
        ], (NamedJSONDecoder, IdentifiableJSONDecoder)).build()

        employee = _Employee()
        employee.name = "Bob"
        employee.id = 42
        employee.title = "Software Dev"
        employee_as_json = {
            "name": employee.name,
            "id": employee.id,
            "title": employee.title
        }
        employee_as_json_string = json.dumps([employee_as_json])
        self.assertEqual(EmployeeJSONDecoder().decode(employee_as_json_string), [employee])


class TestSetJSONEncoderClassBuilder(unittest.TestCase):
    """
    Tests for `SetJSONEncoderClassBuilder`.
    """
    def setUp(self):
        self.values = set([create_simple_model_with_json_representation(i)[0] for i in range(10)])
        self.values_as_json = [create_simple_model_with_json_representation(i)[1] for i in range(10)]
        self.ValueJSONEncoder = MappingJSONEncoderClassBuilder(
            SimpleModel, get_simple_model_json_property_mappings()).build()

    def test_build(self):
        CustomSetJSONEncoder = SetJSONEncoderClassBuilder(self.ValueJSONEncoder).build()
        encoder = CustomSetJSONEncoder()    # type: JSONEncoder
        self.assertCountEqual(encoder.default(self.values), self.values_as_json)


class TestSetJSONDecoderClassBuilder(unittest.TestCase):
    """
    Tests for `SetJSONDecoderClassBuilder`.
    """
    def setUp(self):
        self.values = set([create_simple_model_with_json_representation(i)[0] for i in range(10)])
        self.values_as_json = [create_simple_model_with_json_representation(i)[1] for i in range(10)]
        self.ValueJSONDecoder = MappingJSONDecoderClassBuilder(
            SimpleModel, get_simple_model_json_property_mappings()).build()

    def test_build(self):
        CustomSetJSONDecoder = SetJSONDecoderClassBuilder(self.ValueJSONDecoder).build()
        decoder = CustomSetJSONDecoder()    # type: JSONDecoder
        values_as_json_string = json.dumps(self.values_as_json)
        self.assertEqual(decoder.decode(values_as_json_string), self.values)


if __name__ == "__main__":
    unittest.main()
