from typing import List

from hgicommon.models import Model


class SimpleModel(Model):
    """
    Example of a simple model.
    """
    def __init__(self, constructor_b=None):
        self.a = None
        self.b = constructor_b


class ComplexModel(SimpleModel):
    """
    Example of a complex model.
    """
    def __init__(self, constructor_b):
        super().__init__(constructor_b)
        self.c = None
        self.d = [SimpleModel(constructor_b + i) for i in range(3)]
        self.e = [4.1, 5.2, 6.3]
        self.f = {"1": 2, "3": 4}
        self.g = "test"
        self.h = 123

        for i in range(len(self.d)):
            self.d[i].a = i

    def all(self) -> List:
        return [self.a, self.b, self.c, self.d]
