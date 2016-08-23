[![Build Status](https://travis-ci.org/wtsi-hgi/python-json.svg)](https://travis-ci.org/wtsi-hgi/python-json)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/python-json/graph/badge.svg)](https://codecov.io/gh/wtsi-hgi/python-json/)
[![Documentation Status](https://readthedocs.org/projects/hgi-json/badge/?version=latest)](http://hgi-json.readthedocs.io/en/latest/?badge=latest)
       

# HGI JSON
A Python 3 library for easily JSON encoding/decoding complex class-based Python models, using an arbitrarily complex 
(but easy to write!) mapping schema.


## Features
* Ability to create serializers and deserializers for complex class-based models using a mapping schema.
* Works seamlessly with Python's in-built `json.dumps` and `json.loads` serialization methods - does not require the use
of exotic "convert_to_json"/"convert_from_json" methods.
* Python models are not be coupled to the serialization process - models do not have to inherit from a particular
superclass or implement an interface with a "to_json" (or similar) method.
* JSON representations produced are not coupled to the Python model - an arbitrary mapping between the JSON and the
model can be defined.
* Simple to define serialization of subclasses, based on how superclasses are serialized.
* Pure Python 3 - no DSL, XML or similar required to describe mappings, not using outdated Python 2.
* [Well tested](https://codecov.io/gh/wtsi-hgi/python-json/).


## Overview
1. Define schema for mapping an object to and/or from JSON representation using a list of `JsonPropertyMapping`
definitions.
2. Use `MappingJSONEncoderClassBuilder` with the mappings to build a subclass of `JSONEncode` for serializing instances 
of a specific type. Similar with decode.
3. Use created encoder class with Python's in-built `json.dumps` via the `cls` parameter. Similar with decoder.


A mapping can be written that allows complex classes, such as that below, to be mapped to and from any JSON
representation:
```python
class CustomClass(SupportFor, MultipleInheritance):
    self __init__(self, support_for_constructor_parameters):
    self.support_for_all_types_of_properties = ""
    self.including_sets = set()
    self.and_lists = list()
    self.and_dictionaries = dict()
    self.and_complex_properties = ComplexClass()
    self.and_nested_objects_of_the_same_type = CustomClass()
    self.and_properties_not_in_json_if_none = None

    self support_for_setters(self, value):
        """..."""

    self support_for_getters(self):
        """..."""
        
CustomClassJSONEncoder = MappingJSONEncoderClassBuilder(...).build()    # type: JSONEncoder
CustomClassJSONDecoder = MappingJSONDecoderClassBuilder(...).build()    # type: JSONDecoder

custom_class_as_json = json.dumps(custom_class, cls=CustomClassJSONEncoder)     # type: str
custom_class = json.loads("<custom_class_as_json>", cls=CustomClassJSONDecoder)     # type: CustomClass
```

## Documentation
[View on ReadTheDocs](http://hgi-json.readthedocs.io/en/readthedocs/) or read in `/docs`.
