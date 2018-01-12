# Functionality
## One-to-one JSON property to object property mapping
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


## Arbitrary mapping to JSON property value
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


## Arbitrary mapping to object property value
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


## Deserializing objects with constructors parameters
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


## Deserializing objects with mutators
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


## Conditionally optional JSON properties
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


## Inheritance
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


## Nested complex objects
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

If a property is encoded/decoded by the same encoder/decoder that is currently being defined, the type should be 
returned by a function to work around the scoping problem, e.g.:
```python
class Person:
   def __init__(self):
       self.nemesis = None

PersonJSONEncoder = MappingJSONEncoderClassBuilder(Person, [
    JsonPropertyMapping("nemesis", "nemesis", encoder_cls=lambda: PersonJSONEncoder)
]).build()
```


## One-way mappings
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

## Casting JSON primitives
To help with casting JSON primitives, the following decoders/encoders are provided:

- `StrJSONEncoder`: serializes value to a string (e.g. object property=`123` -> JSON property=`"123"`).
- `StrJSONDecoder`: deserializes value as a string (e.g. JSON property=`123` -> object property=`"123"`).
- `IntJSONEncoder`: serializes value to an int (e.g. object property=`"123"` -> JSON property=`123`).
- `IntJSONDecoder`: deserializes value as an int (e.g. JSON property=`"123"` -> object property=`123`).
- `FloatJSONEncoder`: serializes value to a float (e.g. object property=`"123.5"` -> JSON property=`123.5`).
- `FloatJSONDecoder`: deserializes value as an float (e.g. JSON property=`"12.3"` -> object property=`12.3`).
- `DatetimeEpochJSONEncoder`: serializes datetime to epoch, truncated to seconds (e.g. object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)` -> JSON property=`0`).
- `DatetimeEpochJSONDecoder`: deserializes datetime as epoch (e.g. JSON property=`0` -> object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)`).
- `DatetimeISOFormatJSONEncoder`: serializes datetime to a ISO 8601 datetime representation (e.g. object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)` -> JSON property=`1970-01-01T00:00:00+00:00`).
- `DatetimeISOFormatJSONDecoder`: deserializes ISO 8601 datetime representation to a datetime (e.g. JSON property=`"1970-01-01T00:00:00+00:00"` -> object property=`datetime(1970, 1, 1, tzinfo=timezone.utc)`).

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

## Optional parameters
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

## Sets and Other Collections
The library supports the easy conversion of `set`s and other collections (including non-inbuilt ones) into JSON arrays.  
The `collection_factory` property can be used to indicate the collection type, where the decoded items are given as the
first argument and the collection is returned. The `collection_iter` can be given if the collection does not implement
the `Iterable` interface; it must take the collection as the first argument and return an iterator for the collection's 
items. 

Model:
```python
class Person:
    def __init__(self, names: Iterable[str]):
        self.nicknames = set(names)
```

JSON (`Person({"Rob", "Bob"})`):
```json
{
    "short_names": ["Bob", "Rob"]
}
```

To define that:
* The JSON "short_names" property is set from the person object's "nicknames" property, which is of type `set`.
* The person object's "nicknames" property is set from the JSON's "short_names" property.
```python
person_mapping = [
    JsonPropertyMapping("short_names", "nicknames", "names", collection_factory=set)
]
````


## Serialization to/from a dict
To serialize an object to a dictionary, opposed to a string:
```python
custom_object_as_dict = CustomJSONEncoder().default(custom_object)  # type: dict
```
*You can use this with any encoder that inherits from `JSONEncoder` and overrides `default`.*

To deserialize an object from a dictionary, opposed to from a string:
```python
custom_object = CustomJSONDecoder().decode_parsed(custom_object_as_dict)
```
*You can only use this with decoders defined by this library as they implement the 
[`ParsedJSONDecoder`](https://github.com/wtsi-hgi/python-json/blob/master/hgijson/json/interfaces.py) interface. To 
achieve this functionality with other `JSONDecoder` implementations, you would have to (wastefully) convert the 
dictionary to a string using `json.dump` before using the decoder's standard `decode` method.*
