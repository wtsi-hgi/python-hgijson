[![Build Status](https://travis-ci.org/wtsi-hgi/python-json.svg)](https://travis-ci.org/wtsi-hgi/python-json)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/python-json/graph/badge.svg)](https://codecov.io/gh/wtsi-hgi/python-json/)


# Python 3 JSON Serialization
Python library for easily JSON encoding/decoding complex class-based Python models, using an arbitrarily complex (but
easy to write!) mapping schema.


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
        self.and_properties_not_in_json_if_none = None

    self support_for_setters(self, value):
        ...

    self support_for_getters(self):
        ...
        
CustomClassJSONEncoder = MappingJSONEncoderClassBuilder(...).build()    # type: JSONEncoder
CustomClassJSONDecoder = MappingJSONDecoderClassBuilder(...).build()    # type: JSONDecoder

custom_class_as_json = json.dumps(custom_class, cls=CustomClassJSONEncoder)     # type: str
custom_class = json.loads("<custom_class_as_json>", cls=CustomClassJSONDecoder)     # type: CustomClass
```

## How to use
### Installation
Stable releases can be installed via PyPI:
```bash
$ pip3 install hgijson
```

Bleeding edge versions can be installed directly from GitHub:
```bash
$ pip3 install git+https://github.com/wtsi-hgi/python-json.git@<commit_id_or_branch_or_tag>#egg=hgijson
```

To declare this library as a dependency of your project, add it to your `requirement.txt` file.



### Imports
All methods and classes can be imported with:
```python
from hgijson import *
```
Once what is required is known, [it is good practice]
(http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html#importing) to import things explicitly, e.g.:
```python
from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
```


### Functionality
- [One-to-one JSON property to object property mapping](#one-to-one-json-property-to-object-property-mapping)
- [Arbitrary mapping to JSON property value](#arbitrary-mapping-to-json-property-value)
- [Arbitrary mapping to object property value](#arbitrary-mapping-to-object-property-value)
- [Deserializing objects with constructors parameters](#deserializing-objects-with-constructors-parameters)
- [Deserializing objects with mutators](#deserializing-objects-with-mutators)
- [Conditionally optional JSON properties](#conditionally-optional-json-properties)
- [Inheritance](#inheritance)
- [Nested complex objects](#nested-complex-objects)
- [One-way mappings](#one-way-mappings)
- [Casting JSON "primitives"](#casting-json-primitives)
- [Optional parameters](#optional-parameters)
- [Sets](#sets)
- [Serialization to/from a `dict`](#serialization-tofrom-a-dict)


#### One-to-one JSON property to object property mapping
Model:
```python
class Person:
    def __init__(self):
        self.name = "Bob Smith"
```

JSON:
```json
{
    "full_name": "<person.name>"
}
```

To define that:
* The JSON "full_name" property is set from the object's "name" property.
* The object's "name" property is set from the JSON's "full_name" property.
```python
mapping_schema = [
    JsonPropertyMapping("full_name", "name")
]
```

Build classes that can serialize/deserialize `Person` instances:
```python
PersonJSONEncoder = MappingJSONEncoderClassBuilder(Person, mapping_schema).build()
PersonJSONDecoder = MappingJSONDecoderClassBuilder(Person, mapping_schema).build()
```

Serialize/deserialize instance of `Person` using Python's inbuilt `json.dumps` and `json.loads`:
```python
person_as_json = json.dumps(person, cls=PersonJSONEncoder)
person = json.loads("<person_as_json>", cls=PersonJSONDecoder)
```


#### Arbitrary mapping to JSON property value
Model:
```python
class Person:
    def __init__(self):
        self.name = "Bob Smith"

    def get_first_name(self) -> str:
        return self.name.split(" ")[0]
        
    def get_family_name(self) -> str:
        return self.name.split(" ")[1]
```

JSON:
```json
{
    "first_name": "<person.get_first_name()>",
    "family_name": "<person.get_family_name()>"
}
```

To define that:
* Serialization to the JSON "first_name" property value uses the object's `get_first_name` method.
* Serialization to the JSON "family_name" property value uses the object's `get_family_name` method.
```python
mapping_schema = [
    JsonPropertyMapping("first_name", object_property_getter=lambda person: person.get_first_name()),
    JsonPropertyMapping("family_name", object_property_getter=lambda person: person.get_family_name())
]
```
*See [next section](#arbitrary-mapping-to-object-property-value) for how to do the reverse mapping.*


#### Arbitrary mapping to object property value
Model:
```python
class Person:
    def __init__(self):
        self.name = None
```

JSON:
```json
{
    "first_name": "<person.name.split(' ')[0]>",
    "family_name": "<person.name.split(' ')[1]>"
}
```

To define that:
* The object's name property value is derived from the value of both the "first_name" and "family name" JSON property 
values:
```python
mapping_schema = [
    JsonPropertyMapping("name", json_property_getter=lambda obj_as_dict: "%s %s" % (obj_as_dict["first_name"],
                                                                                    obj_as_dict["family_name"]))
]
```


#### Deserializing objects with constructors parameters
Model:
```python
class Person:
    def __init__(self, constructor_name: str):
        self.name = name
```

JSON:
```json
{
    "full_name": "<person.name>"
}
```

To define that:
* Deserialization requires the value of the JSON "full_name" property be binded to the "constructor_name" parameter
in the constructor.
* Serialization to the JSON "full_name" property value uses the object's "name" property value.
```python
mapping_schema = [
    JsonPropertyMapping("full_name", "name", object_constructor_parameter_name="constructor_name")
]
```

If further modification of the decoded value is needed, `object_constructor_argument_modifier` can be set as a function
that takes the value retrieved by `json_property_getter` after it is decoded by using the `decoder_cls` JSON encoder and
returns the value that is binded to the constructor parameter.


#### Deserializing objects with mutators
Model:
```python
class Person:
    def __init__(self):
        self._name = None
        
    def set_name(name: str):
        self._name = name
```

JSON:
```json
{
    "full_name": "<person._name>"
}
```

To define that:
* Deserialization requires the private "_name" property be set via the "set_name" mutator from the "full_name" JSON
property.
```python
mapping_schema = [
    JsonPropertyMapping("full_name", object_property_setter=lambda person, name: person.set_name(name))
]
```


#### Conditionally optional JSON properties
Model:
```python
class Person:
    def __init__(self):
        self.name = name
```

JSON:
```javascript
// if person.name is not None:
{
    "full_name": "<person.name>"
}
// else:
{
    // No `full_name` property
}
```

To define that:
* JSON representation should only include the "full_name" if it is not `None` (e.g. to reduce the size of the JSON).
```python
def add_name_to_json_if_not_none(json_as_dict: dict, name: Optional[str]):
    if name is not None:
        json_as_dict["full_name"] = name

mapping_schema = [JsonPropertyMapping("full_name", json_property_setter=add_name_to_json_if_not_none)]
```


#### Inheritance
Models:
```python        
class Identifiable:
    def __init__(self):
        self.id = None

class Named:
    def __init__(self):
        self.name = None
   
class Employee(Identifiable, Named):
    def __init__(self):
        super().__init__()
        self.title = None
```

JSON:
```json
{
    "identifier": "<employee.id>",
    "full_name": "<employee.name>",
    "job_title": "<employee.title>"
}
```

To define that:
* Serialization of `Employee` should "extend" the way `Named` and `Identifiable` are serialized.
```python
identifiable_mapping_schema = [JsonPropertyMapping("identifier", "id")]
named_mapping_schema = [JsonPropertyMapping("full_name", "name")]
employee_mapping_schema = [JsonPropertyMapping("job_title", "title")]

IdentifiableJSONEncoder = MappingJSONEncoderClassBuilder(Identifiable, identifiable_mapping_schema).build()
NamedJSONEncoder = MappingJSONEncoderClassBuilder(Named, named_mapping_schema).build()
EmployeeJSONEncoder = MappingJSONEncoderClassBuilder(Employee, employee_mapping_schema, (IdentifiableJSONEncoder, NamedJSONEncoder)).build()

IdentifiableJSONDecoder = MappingJSONDecoderClassBuilder(Identifiable, identifiable_mapping_schema).build()
NamedJSONDecoder = MappingJSONDecoderClassBuilder(Named, named_mapping_schema).build()
EmployeeJSONDecoder = MappingJSONDecoderClassBuilder(Employee, employee_mapping_schema, (IdentifiableJSONDecoder, NamedJSONDecoder)).build()
```

Note: Each value mapping can be "overriden" by encoders used afterwards. Mappings of properties for superclasses are 
done before those defined in the current class; the mappings for superclasses are completed in the order defined by the
tuple. e.g. In the example above, the mappings defined in `IdentifiableJSONDecoder` are applied first, then those in
`NamedJSONDecoder`, followed by those in `EmployeeJSONDecoder`. If `EmployeeJSONDecoder` redefined a mapping for the 
`id` object property, the value for this property would first be written by the mapper from `IdentifiableJSONDecoder` 
before been overwritten by a mapper defined in `EmployeeJSONDecoder`.

For obvious reasons, the mappings to constructor parameters defined in superclasses are not used.


#### Nested complex objects
Model:
```python
class Person:
    def __init__(self):
        self.name = None

class Team:
    def __init__(self):
        self.moto = None
        self.people = []    # type: List[Person]
```

JSON:
```json
{
    "team_moto": "<team.moto>",
    "members": "<[person in team.people]>"
}
```

To define that:
* `Person` instances, nested inside `Employee` objects, should be serialized and deserialized by specific encoder and 
decoders.
```python
employee_mapping_schema = [
    JsonPropertyMapping("team_moto", "moto"),
    JsonPropertyMapping("members", "people", encoder_cls=PersonJSONEncoder, decoder_cls=PersonJSONDecoder)
]
```


#### One-way mappings
*Contrived example warning...*

Model:
```python
class Person:
    def __init__(self):
        self.name = None
        self.age = None
```

JSON input:
```json
{
    "full_name": "<person.name>"
}
```

JSON output:
```json
{
    "age": "<person.age>"
}
```

To define that:
* Serialization should ignore the object's "name" property.
* Deserialization only with the JSON's "full_name" property.
```python
mapping_schema = [
    JsonPropertyMapping(
        json_property_getter=lambda json_as_dict: json_as_dict["full_name"],
        object_property_setter=lambda person, name: person.set_name(name)
    ),
    JsonPropertyMapping(
        json_property_setter=lambda json_as_dict, age: json_as_dict.__setitem__("age", age),
        object_property_getter=lambda person: person.age
    )
]
```

#### Casting JSON primitives
To help with casting JSON primitives, the following decoders/encoders are provided:
* `StrJSONEncoder`: serializes value to a string (e.g. object property=`123` -> JSON property=`"123"`).
* `StrJSONDecoder`: deserializes value as a string (e.g. JSON property=`123` -> object property=`"123"`).
* `IntJSONEncoder`: serializes value to an int (e.g. object property=`"123"` -> JSON property=`123`).
* `IntJSONDecoder`: deserializes value as an int (e.g. JSON property=`"123"` -> object property=`123`).
* `FloatJSONEncoder`: serializes value to a float (e.g. object property=`"123.5"` -> JSON property=`123.5`).
* `FloatJSONDecoder`: deserializes value as an float (e.g. JSON property=`"12.3"` -> object property=`12.3`).
* `DatetimeEpochJSONEncoder`: serializes datetime to epoch, truncated to seconds (e.g. object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)` -> JSON property=`0`).
* `DatetimeEpochJSONDecoder`: deserializes datetime as epoch (e.g. JSON property=`0` -> object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)`).
* `DatetimeISOFormatJSONEncoder`: serializes datetime to a ISO 8601 datetime representation (e.g. object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)` -> JSON property=`1970-01-01T00:00:00+00:00`).
* `DatetimeISOFormatJSONDecoder`: deserializes ISO 8601 datetime representation to a datetime (e.g. JSON property=`"1970-01-01T00:00:00+00:00"` -> object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)`).

Model:
```python
class Person:
    def __init__(self):
        self.age = 42
```

JSON:
```json
{
    "years_old": "str(<person.age>)"
}
```

To define that:
* The age property of `Person` instances should be an `int` but given as a string in the JSON representation.
```python
person_mapping_schema = [
    JsonPropertyMapping("years_old", "age", encoder_cls=StrJSONEncoder, decoder_cls=IntJSONDecoder)
]
```

#### Optional parameters
Model:
```python
class Person:
    def __init__(self):
        self.name = None
        self.age = 42
```

JSON:
```json
{
    "years_old": "<person.age>"
}
```

To define that:
* A JSON parameter is optional (i.e. it may/may not appear in the JSON representation).
* An object parameter should not be included in the JSON if it takes the value `None`.
```python
person_mapping_schema = [
    JsonPropertyMapping("full_name", "name", optional=True), 
    JsonPropertyMapping("years_old", "age")
]
```

#### Sets
JSON supports less "primitive types" than Python, implying that there cannot be an unambiguous, one-to-one mapping
between all Python and JSON "primitive types". One such type without an equivalent in JSON is `set`. Python's built-in 
JSON library "handles" the serialiation of sets by raising a `TypeError`.

`SetJSONEncoder` and `SetJSONDecoder` are supplied in this library to support the serialization of `set`s. They work by
encoding sets as JSON lists then decoding these lists back into sets. As the mapping between JSON and objects is well 
defined when using this library (i.e. it never has to guess the type of the Python object that is to be constructed from
a JSON representation), it is known if a JSON list should be decoded as `list` or as `set`.

Build classes that can serialize/deserialize sets of strings:
```python
StringSetJSONEncoder = SetJSONEncoderClassBuilder(StrJSONEncoder).build()
StringSetJSONDecoder = SetJSONDecoderClassBuilder(StrJSONDecoder).build()
```

Model:
```python
class Person:
    def __init__(self):
        self.nicknames = {"Rob", "Bob"}
```

JSON:
```json
{
    "short_names": ["<person.nicknames>"]
}
```

To define that:
* The JSON "short_names" property is set from the object's "nicknames" property, which is of type `set`.
* The object's "nicknames" property is set from the JSON's "full_name" property.
```python
mapping_schema = [
    JsonPropertyMapping("short_names", "nicknames", encoder_cls=StringSetJSONEncoder, decoder_cls=StringSetJSONDecoder)
]
```


#### Serialization to/from a `dict`
To serialize an object to a dictionary, opposed to a string:
```python
custom_object_as_dict = CustomJSONEncoder().default("<custom_object>")  # type: dict
```
*You can use this with any encoder that inherits from `JSONEncoder` and overrides `default`.*

To deserialize an object from a dictionary, opposed to from a string:
```python
custom_object = CustomJSONDecoder().decode_parsed("<custom_object_as_dict>")
```
*You can only use this with decoders defined by this library as they implement the [`ParsedJSONDecoder`]
(https://github.com/wtsi-hgi/python-json/blob/master/hgijson/json/interfaces.py) interface. To achieve this
functionality with other `JSONDecoder` implementations, you would have to (wastefully) convert the dictionary to a 
string using `json.dump` before using the decoder's standard `decode` method.*


### Notes
* Decoders and encoders work for iterable collections of instances in the same way as they do for single instances.
* Encoders will only encode objects into JSON objects (`{}`). A custom `JSONEncoder` must be used to encode Python 
objects that should be represented in any other way (e.g. as a JSON list (`[]`)).
* Ensure your serializers are not vulnerable to attack if you are serializing JSON from an untrusted source.


## Performance
If you are performing serialization, chances are that you are going to be doing/have done I/O. Given how relatively slow
the I/O will be, the performance of this library, compared with that of any other (including the endless JSON
libraries touted as "ultra fast"), **is not going to be of realistic concern** given reasonable amounts of data.

However, if you happen to be serializing huge numbers of objects and need it done extraordinarily fast (in Python?), 
bare in mind that use of JSON encoders/decoders produced by this library will add a small amount of overhead on-top of 
the in-built JSON serialization methods. In addition, the complexity of the mappings used will influence the performance
(i.e. if the value of a JSON property is calculated from an object method that deduces the answer to life, the universe 
and everything, serialization is going to be rather slow).


## Alternatives
* If you are not using class-based Python models and have no restrictions on the structure of the JSON representation:
    * [Python's in-built `json` library](https://docs.python.org/3/library/json.html) will work out the box with its 
    default encoder (`JSONEncode`) and decoder (`JSONDecode`).
    * [demjson](https://github.com/dmeranda/demjson) can encode and decode JSON with added syntax checking.
    * [ultrajson](https://github.com/esnme/ultrajson) is claimed as an "ultra fast" JSON encoder and decoder.
    * [py-yajl](https://github.com/rtyler/py-yajl) is yet another "fast" JSON encoder/decoder.
* If you are using class-based Python models but your JSON need not be human readable and you are not concerned with
interoperability:
    * [jsonpickle](https://github.com/jsonpickle/jsonpickle) will automatically serialize objects.
    * [py-importjson](https://github.com/TonyFlury/py-importjson).
* If you want to deserialize flat data files into Python `dict` objects using mapping schema:
    * [jsonmapping](https://github.com/pudo/jsonmapping)
* If you do not mind coupling your Python models to the serialization library:
    * [jsonobject](https://github.com/dimagi/jsonobject).
* If you only wish to serialize models using a mapping schema and are not interested in deserialization or compatibility
with Python's in-built `json` library.
    * [serpy](https://github.com/clarkduvall/serpy) can serialize complex models with arbitrary mappings from fields and
    methods to JSON.


## Development
### Setup
Install both library dependencies and the dependencies needed for testing:
```bash
$ pip3 install -q -r requirements.txt
$ pip3 install -q -r test_requirements.txt
```

### Testing
Using nosetests, in the project directory, run:
```bash
$ nosetests -v
```

To generate a test coverage report with nosetests:
```bash
$ nosetests -v --with-coverage --cover-package=hgijson --cover-inclusive
```


## License
[MIT license](LICENSE.txt).

Copyright (c) 2015, 2016 Genome Research Limited