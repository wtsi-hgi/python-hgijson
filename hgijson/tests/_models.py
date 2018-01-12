from abc import ABCMeta


class BaseModel(metaclass=ABCMeta):
    """
    TODO
    """
    def __str__(self) -> str:
        string_builder = []
        for property, value in vars(self).items():
            string_builder.append("%s: %s" % (property, str(value)))
        string_builder = sorted(string_builder)
        return "{ %s }" % ', '.join(string_builder)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        if type(other) != type(self):
            return False
        for property, value in vars(self).items():
            other_value = getattr(other, property, object())
            if other_value != value:
                return False
        return True

    def __hash__(self):
        return hash(str(self))


class SimpleModel(BaseModel):
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
        self.i = {3, 1, 4, 1, 5, 9}

        for i in range(len(self.d)):
            self.d[i].a = i
