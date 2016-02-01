import json
import unittest
from numbers import Complex

from hgicommon.serialization.json._serialization import MappingJSONEncoder, MappingJSONDecoder
from hgicommon.serialization.json.builders import MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
from hgicommon.tests._stubs import StubModel
from hgicommon.tests.serialization._models import SimpleModel, ComplexModel
from hgicommon.tests.serialization.json._helpers import create_complex_model_with_json_representation,\
    create_simple_model_with_json_representation
from hgicommon.tests.serialization.json._serializers import get_simple_model_json_property_mappings, \
    get_complex_model_json_property_mappings


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
        encoder = encoder_cls() # type: MappingJSONEncoder

        encoded = encoder.default(self.simple_model)
        self.assertDictEqual(encoded, self.simple_model_as_json)

    def test_build_with_superclass(self):
        SimpleModelJSONEncoder = MappingJSONEncoderClassBuilder(
            target_cls=SimpleModel, mappings=get_simple_model_json_property_mappings()).build()

        encoder_builder = MappingJSONEncoderClassBuilder()
        encoder_builder.superclass = SimpleModelJSONEncoder
        encoder_builder.target_cls = ComplexModel
        encoder_builder.mappings = get_complex_model_json_property_mappings()

        encoder_cls = encoder_builder.build()
        encoder = encoder_cls()     # type: MappingJSONEncoder

        encoded = encoder.default(self.complex_model)
        self.assertDictEqual(encoded, self.complex_model_as_json)


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
        decoder_builder.superclass = SimpleModelJSONDecoder
        decoder_builder.target_cls = ComplexModel
        decoder_builder.mappings = get_complex_model_json_property_mappings()

        decoder_cls = decoder_builder.build()
        decoder = decoder_cls()     # type: MappingJSONDecoder

        decoded = decoder.decode(json.dumps(self.complex_model_as_json))
        self.assertEqual(decoded, self.complex_model)


if __name__ == "__main__":
    unittest.main()
