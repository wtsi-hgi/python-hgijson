from typing import List

from hgicommon.models import Model


class SimpleModel(Model):
    def __init__(self, constructor_b=None):
        self.a = None
        self.b = constructor_b


class ComplexModel(SimpleModel):
    def __init__(self, constructor_b):
        super().__init__(constructor_b)
        self.c = None
        self.d = SimpleModel(constructor_b)

    def all(self) -> List:
        return [self.a, self.b, self.c, self.d]
