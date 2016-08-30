# Examples
## Example 1: The Employee
### The Models
```python
from abc import ABCMeta
from hgicommon.models import Model

class Named(Model, metaclass=ABCMeta):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class Identifiable(Model, metaclass=ABCMeta):
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id


class Office(Named):
    def __init__(self, name: str):
        super().__init__(name)


class Employee(Named, Identifiable):
    def __init__(self, name: str, id: int, title: str=None, office: Office=None):
        super().__init__(name=name, id=id)
        self.title = title
        self.office = office
```

### The Encoders and Decoders
```python
from hgijson import MappingJSONDecoderClassBuilder, MappingJSONEncoderClassBuilder, JsonPropertyMapping

# Defines encoder and decoder for instances of `Named`
named_mappings = [
    JsonPropertyMapping("name", "name", "name")
]
NamedJSONDecoder = MappingJSONDecoderClassBuilder(Named, named_mappings).build()
NamedJSONEncoder = MappingJSONEncoderClassBuilder(Named, named_mappings).build()


# Defines encoder and decoder for instances of `Identifiable`
identifiable_mappings = [
    JsonPropertyMapping("identification_number", "id", "id")
]
IdentifiableJSONEncoder = MappingJSONEncoderClassBuilder(Identifiable, identifiable_mappings).build()
IdentifiableJSONDecoder = MappingJSONDecoderClassBuilder(Identifiable, identifiable_mappings).build()


# Defines encoder and decoder for instances of `Office`
OfficeJSONEncoder = MappingJSONDecoderClassBuilder(Office, [], (NamedJSONEncoder,)).build()
OfficeJSONDecoder = MappingJSONDecoderClassBuilder(Office, [], (NamedJSONDecoder,)).build()


# Defines encoder and decoder for instances of `Employee`
employee_mappings = [
    JsonPropertyMapping("job_title", "title"),
    JsonPropertyMapping("location", "office", encoder_cls=OfficeJSONEncoder, decoder_cls=OfficeJSONDecoder)
]
EmployeeJSONEncoder = MappingJSONEncoderClassBuilder(Employee, employee_mappings, (NamedJSONEncoder, IdentifiableJSONEncoder)).build()
EmployeeJSONDecoder = MappingJSONDecoderClassBuilder(Employee, employee_mappings, (NamedJSONDecoder, IdentifiableJSONDecoder)).build()
```


#### Results
```python
import json

office = Office("Bob's Office")
bob = Employee("Bob", 123, "Software Developer", office)

bob_as_json_string = json.dumps(bob, cls=EmployeeJSONEncoder, indent=4, sort_keys=True)
print(bob_as_json_string)
```
```json
{
    "identification_number": 123,
    "job_title": "Software Developer",
    "location": {
        "name": "Bob's Office"
    },
    "name": "Bob"
}
```

```python
bob_deserialised = json.loads(bob_as_json_string, cls=EmployeeJSONDecoder) 
print(bob_deserialised == bob)
```
```python
True
```


