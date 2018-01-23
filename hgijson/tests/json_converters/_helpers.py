from typing import Dict, Tuple

from hgijson.tests._models import SimpleModel, ComplexModel

EXAMPLE_VALUE_1 = "example-value-1"
EXAMPLE_VALUE_2 = "example-value-2"
EXAMPLE_VALUE_3 = "example-value-3"
EXAMPLE_VALUE_4 = "example-value-4"

EXAMPLE_PROPERTY_1 = "example-property-1"
EXAMPLE_PROPERTY_2 = "example-property-2"
EXAMPLE_PROPERTY_3 = "example-property-3"
EXAMPLE_PROPERTY_4 = "example-property-4"


def create_simple_model_with_json_representation(modifier: int=0) -> Tuple[SimpleModel, Dict]:
    """
    Creates an instance of `SimpleModel` alongside its expected JSON representation (given the most obvious property
    mappings).
    :param modifier: can be used to make the model distinguishable
    :return: tuple where the first value is the model and the second is its JSON representation
    """
    simple_model = SimpleModel(50)
    simple_model.a = modifier

    simple_model_as_json = {
        "serialized_a": simple_model.a,
        "serialized_b": simple_model.b
    }

    return simple_model, simple_model_as_json


def create_complex_model_with_json_representation(modifier: int=0) -> Tuple[ComplexModel, Dict]:
    """
    Creates an instance of `ComplexModel` alongside its expected JSON representation (given the most obvious property
    mappings).
    :param modifier: can be used to make the model distinguishable
    :return: tuple where the first value is the model and the second is its JSON representation
    """
    complex_model = ComplexModel(5)
    complex_model.a = modifier
    complex_model.c = 4

    complex_model_as_json = create_simple_model_with_json_representation(modifier)[1]
    complex_model_as_json.update({
        "serialized_a": complex_model.a,
        "serialized_b": complex_model.b,
        "serialized_c": complex_model.c,
        "serialized_d": [{
            "serialized_a": i,
            "serialized_b": complex_model.b + i
        } for i in range(3)],
        "serialized_e": complex_model.e,
        "serialized_f": complex_model.f,
        "serialized_g": complex_model.g,
        "serialized_h": complex_model.h,
        "serialized_i": list(complex_model.i)
    })

    return complex_model, complex_model_as_json
