# Examples
## Example 1: The Employee
### The Models
```python
from abc import ABCMeta

class Named(metaclass=ABCMeta):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class Identifiable(metaclass=ABCMeta):
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
assert bob_deserialised == bob
```


## Example 2: Sets and Collections
### The Models
```python
from typing import Iterable, Set

class Person:
    def __init__(self, names: Iterable[str]):
        self.nicknames = set(names)

    def __eq__(self, other):
        return type(other) == type(self) and other.nicknames == self.nicknames

    def __hash__(self):
        return hash("".join(sorted(self.nicknames)))


class WorkerInventory:
    def __init__(self, workers):
        self.workers = workers

    def __iter__(self):
        return iter(self.workers)

    def get_with_nickname(self, nickname: str) -> Set[Person]:
        return {worker for worker in self.workers if nickname in worker.nicknames}


class Company:
    def __init__(self, name, workers):
        self.name = name
        self.workers = workers
```


### The Encoders and Decoders
```python
from hgijson import MappingJSONDecoderClassBuilder, MappingJSONEncoderClassBuilder, JsonPropertyMapping

person_mapping = [
    JsonPropertyMapping("short_names", "nicknames", "names", collection_factory=set)
]
PersonJSONEncoder = MappingJSONEncoderClassBuilder(Person, person_mapping).build()
PersonJSONDecoder = MappingJSONDecoderClassBuilder(Person, person_mapping).build()

company_mapping = [
    JsonPropertyMapping("id", "name", "name"),
    JsonPropertyMapping("workers", "workers", "workers", collection_factory=WorkerInventory, 
                        encoder_cls=PersonJSONEncoder, decoder_cls=PersonJSONDecoder)
]
CompanyJSONEncoder = MappingJSONEncoderClassBuilder(Company, company_mapping).build()
CompanyJSONDecoder = MappingJSONDecoderClassBuilder(Company, company_mapping).build()
```


#### Results
```python
import json

person = Person({"Rob", "Bob"})
company = Company("My Company", [person])
comapny_as_json_string = json.dumps(company, cls=CompanyJSONEncoder, indent=4, sort_keys=True)

print(comapny_as_json_string)
```
```json
{
    "id": "My Company",
    "workers": [
        {
            "short_names": [
                "Bob",
                "Rob"
            ]
        }
    ]
}
```

```python
company = json.loads(comapny_as_json_string, cls=CompanyJSONDecoder) 
bobs = company.workers.get_with_nickname("Bob")
assert len(bobs) == 1
assert list(bobs)[0] == person
```
