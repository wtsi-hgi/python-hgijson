import json
import unittest

from hgijson.json_converters._serialization import MappingJSONDecoder, MappingJSONEncoder
from hgijson.json_converters.builders import MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from hgijson.json_converters.models import JsonPropertyMapping
from hgijson.tests._models import SimpleModel, ComplexModel, BaseModel
from hgijson.tests.json_converters._helpers import create_complex_model_with_json_representation, \
    create_simple_model_with_json_representation
from hgijson.tests.json_converters._serializers import get_simple_model_json_property_mappings, \
    get_complex_model_json_property_mappings


class _Named(BaseModel):
    def __init__(self):
        super().__init__()
        self.name = None    # type: str


class _Office(_Named):
    def __init__(self):
        super().__init__()


class _Identifiable(BaseModel):
    def __init__(self):
        super().__init__()
        self.id = None    # type: int


class _Employee(_Named, _Identifiable):
    def __init__(self):
        super().__init__()
        self.title = None
        self.office = None


class _Container(BaseModel):
    def __init__(self, colour: str, container: "_Container" = None):
        self.colour = colour
        self.contains = container


class TestMappingJSONEncoderClassBuilder(unittest.TestCase):
    """
    Tests for `MappingJSONEncoderClassBuilder`.
    """
    def setUp(self):
        self.simple_model, self.simple_model_as_json = create_simple_model_with_json_representation()
        self.complex_model, self.complex_model_as_json = create_complex_model_with_json_representation()

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

    def test_build_with_superclass_as_string(self):
        ContainerJSONEncoder = MappingJSONEncoderClassBuilder(_Container, [
            JsonPropertyMapping("colour", "colour", object_constructor_parameter_name="colour"),
            JsonPropertyMapping("contains", "contains", encoder_cls=lambda: ContainerJSONEncoder, optional=True)
        ]).build()
        encoder = ContainerJSONEncoder()
        container = _Container("red", _Container("blue"))
        self.assertEqual({"colour": "red", "contains": {"colour": "blue"}}, encoder.default(container))

    def test_build_with_multiple_superclasses(self):
        NamedJSONEncoder = MappingJSONEncoderClassBuilder(_Named, [
            JsonPropertyMapping("name", "name")
        ]).build()
        OfficeJSONEncoder = MappingJSONEncoderClassBuilder(_Office, [], (NamedJSONEncoder, )).build()
        IdentifiableJSONEncoder = MappingJSONEncoderClassBuilder(_Identifiable, [
            JsonPropertyMapping("id", "id")
        ]).build()
        EmployeeJSONEncoder = MappingJSONEncoderClassBuilder(_Employee, [
            JsonPropertyMapping("title", "title"),
            JsonPropertyMapping("office", "office", encoder_cls=OfficeJSONEncoder),
        ], (NamedJSONEncoder, IdentifiableJSONEncoder)).build()

        office = _Office()
        office.name = "Cambridge"

        employee = _Employee()
        employee.name = "Bob"
        employee.id = 42
        employee.title = "Software Dev"
        employee.office = office

        employee_as_json = {
            "name": employee.name,
            "id": employee.id,
            "title": employee.title,
            "office": {
                "name": office.name
            }
        }
        self.assertEqual(EmployeeJSONEncoder().default(employee), employee_as_json)

    def test_build_with_none_property(self):
        NamedJSONEncoder = MappingJSONEncoderClassBuilder(_Named, [
            JsonPropertyMapping("name", "name")
        ]).build()
        OfficeJSONEncoder = MappingJSONEncoderClassBuilder(_Office, [], (NamedJSONEncoder,)).build()
        EmployeeJSONEncoder = MappingJSONEncoderClassBuilder(_Employee, [
            JsonPropertyMapping("office", "office", encoder_cls=OfficeJSONEncoder),
        ], (NamedJSONEncoder, )).build()

        employee = _Employee()
        employee.name = "Bob"
        employee.office = None

        employee_as_json = {
            "name": employee.name,
            "office": None
        }
        self.assertEqual(employee_as_json, EmployeeJSONEncoder().default(employee))


class TestMappingJSONDecoderClassBuilder(unittest.TestCase):
    """
    Tests for `MappingJSONDecoderClassBuilder`.
    """
    def setUp(self):
        self.simple_model, self.simple_model_as_json = create_simple_model_with_json_representation()
        self.complex_model, self.complex_model_as_json = create_complex_model_with_json_representation()

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

    def test_build_with_superclass_string(self):
        ContainerJSONDecoder = MappingJSONDecoderClassBuilder(_Container, [
            JsonPropertyMapping("colour", "colour", object_constructor_parameter_name="colour"),
            JsonPropertyMapping("contains", "contains", decoder_cls=lambda: ContainerJSONDecoder, optional=True)
        ]).build()
        decoder = ContainerJSONDecoder()
        container = _Container("red", _Container("blue"))
        self.assertEqual(container, decoder.decode(json.dumps({"colour": "red", "contains": {"colour": "blue"}})))

    def test_build_with_multiple_superclasses(self):
        NamedJSONDecoder = MappingJSONDecoderClassBuilder(_Named, [
            JsonPropertyMapping("name", "name")
        ]).build()
        OfficeJSONDecoder = MappingJSONDecoderClassBuilder(_Office, [], (NamedJSONDecoder,)).build()
        IdentifiableJSONDecoder = MappingJSONDecoderClassBuilder(_Identifiable, [
            JsonPropertyMapping("id", "id")
        ]).build()
        EmployeeJSONDecoder = MappingJSONDecoderClassBuilder(_Employee, [
            JsonPropertyMapping("title", "title"),
            JsonPropertyMapping("office", "office", decoder_cls=OfficeJSONDecoder)
        ], (NamedJSONDecoder, IdentifiableJSONDecoder)).build()

        office = _Office()
        office.name = "Cambridge"

        employee = _Employee()
        employee.name = "Bob"
        employee.id = 42
        employee.title = "Software Dev"
        employee.office = office

        employee_as_json = {
            "name": employee.name,
            "id": employee.id,
            "title": employee.title,
            "office": {
                "name": office.name
            }
        }
        employee_as_json_string = json.dumps([employee_as_json])
        self.assertEqual(EmployeeJSONDecoder().decode(employee_as_json_string), [employee])

    def test_build_with_none_property(self):
        NamedJSONDecoder = MappingJSONDecoderClassBuilder(_Named, [
            JsonPropertyMapping("name", "name")
        ]).build()
        OfficeJSONDecoder = MappingJSONDecoderClassBuilder(_Office, [], (NamedJSONDecoder,)).build()
        EmployeeJSONDecoder = MappingJSONDecoderClassBuilder(_Employee, [
            JsonPropertyMapping("office", "office", decoder_cls=OfficeJSONDecoder)
        ], (NamedJSONDecoder, )).build()

        employee = _Employee()
        employee.name = "Bob"
        employee.office = None

        employee_as_json = {
            "name": employee.name,
            "id": employee.id,
            "title": employee.title,
            "office": None
        }
        employee_as_json_string = json.dumps([employee_as_json])
        self.assertEqual(EmployeeJSONDecoder().decode(employee_as_json_string), [employee])


if __name__ == "__main__":
    unittest.main()
