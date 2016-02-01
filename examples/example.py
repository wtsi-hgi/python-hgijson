import json
from enum import Enum, unique
from typing import Optional

from typing import List

from hgicommon.models import Model

from hgijson.json.builders import MappingJSONDecoderClassBuilder
from hgijson.json.builders import MappingJSONEncoderClassBuilder
from hgijson.json.models import JsonPropertyMapping


class Person(Model):
    @unique
    class EyeColour(Enum):
        UNKNOWN = 1
        BLUE = 2
        GREEN = 3

    def __init__(self, constructor_name: str="Unknown"):
        self.name = constructor_name
        self.eye_colour = Person.EyeColour.UNKNOWN

    def get_first_name(self) -> str:
        return self.name.split(" ")[0]

    def get_family_name(self) -> str:
        return self.name.split(" ")[1]


class Employee(Person):
    def __init__(self, constructor_worker_id: int, constructor_name: str):
        super().__init__(constructor_name)
        self.worker_id = constructor_worker_id
        # TODO: Add another property to fully demonstate inheritence decoder/encoder


class Company(Model):
    def __init__(self):
        self.name = None
        self.employees = []     # type: List[Employee]

    def generate_moto(self) -> str:
        return "%s is great!" % self.name


eye_colour_enum_to_string = {
    Person.EyeColour.UNKNOWN: None,
    Person.EyeColour.GREEN: "green",
    Person.EyeColour.BLUE: "blue"
}


def set_eye_colour_on_json_if_known(json_representation: dict, eye_colour: Optional[str]):
    if eye_colour is not None:
        json_representation["eye_colour"] = eye_colour


def set_eye_colour_on_person_if_known(person: Person, eye_colour_as_string: Optional[str]):
    if eye_colour_as_string is not None:
        person.eye_colour = [key for key, value in eye_colour_enum_to_string.items() if value == eye_colour_as_string][0]



person_to_json_mappings = [
    JsonPropertyMapping("name", json_property_getter=lambda obj_as_dict: "%s %s" % (obj_as_dict["first_name"],
                                                                                    obj_as_dict["family_name"])),
    JsonPropertyMapping("first_name", object_property_getter=lambda person: person.get_first_name()),
    JsonPropertyMapping("family_name", object_property_getter=lambda person: person.get_family_name()),
    JsonPropertyMapping(json_property_setter=set_eye_colour_on_json_if_known,
                        json_property_getter=lambda json_representation: json_representation.get("eye_colour", None),
                        object_property_getter=lambda person: eye_colour_enum_to_string[person.eye_colour],
                        object_property_setter=set_eye_colour_on_person_if_known)
]
PersonJSONEncoder = MappingJSONEncoderClassBuilder(Person, person_to_json_mappings).build()
PersonJSONDecoder = MappingJSONDecoderClassBuilder(Person, person_to_json_mappings).build()

employee_to_json_mappings = [
    JsonPropertyMapping("name", json_property_getter=lambda obj_as_dict: "%s %s" % (obj_as_dict["first_name"],
                                                                                    obj_as_dict["family_name"]),
                        object_constructor_parameter_name="constructor_name"),
    JsonPropertyMapping("id", "worker_id", "constructor_worker_id")
]
EmployeeJSONEncoder = MappingJSONEncoderClassBuilder(Employee, employee_to_json_mappings, PersonJSONEncoder).build()
EmployeeJSONDecoder = MappingJSONDecoderClassBuilder(Employee, employee_to_json_mappings, PersonJSONDecoder).build()

company_to_json_mappings = [
    JsonPropertyMapping("operating_name", "name"),
    JsonPropertyMapping("moto", object_property_getter=lambda company: company.generate_moto()),
    JsonPropertyMapping("workers", "employees", encoder_cls=EmployeeJSONEncoder, decoder_cls=EmployeeJSONDecoder)
]
CompanyJSONEncoder = MappingJSONEncoderClassBuilder(Company, company_to_json_mappings).build()
CompanyJSONDecoder = MappingJSONDecoderClassBuilder(Company, company_to_json_mappings).build()

company = Company()
company.name = "The JSON Company"
company.employees.append(Employee(1, "Bob Smith"))
company.employees.append(Employee(2, "John Doe"))

company.employees[0].eye_colour = Person.EyeColour.GREEN

company_as_json_1 = json.dumps(company, cls=CompanyJSONEncoder)
comapany_decoded_from_json = json.loads(company_as_json_1, cls=CompanyJSONDecoder)
company_as_json_2 = json.dumps(comapany_decoded_from_json, cls=CompanyJSONEncoder, indent=1)

print(company_as_json_2)
"""
```
{
    "operating_name": "The JSON Company",
    "moto": "The JSON Company is great!"
    "workers": [
        {
            "id": 1,
            "first_name": "Bob"
            "second_name": "Smith"
        },
        {
            "id": 2,
            "first_name": "John"
            "second_name": "Doe"
        }
    ]
}
```
"""