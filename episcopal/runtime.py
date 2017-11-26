from typing import Iterable, List

from treadmill import Cell


class RuntimeObject:
    def children(self) -> Iterable[Cell]:
        return ()


class Integer(RuntimeObject):
    def __init__(self, value: int):
        self.value = value


class Double(RuntimeObject):
    def __init__(self, value: float):
        self.value = value


class Percentage(RuntimeObject):
    def __init__(self, value: float):
        self.value = value


class Boolean(RuntimeObject):
    def __init__(self, value: bool):
        self.value = value


class Distribution(RuntimeObject):
    def __init__(self, type: int, n: int, elements: List[Cell]):
        self.type = type
        self.n = n
        self.elements = elements

    def children(self):
        return self.elements


class ParamDistribution(RuntimeObject):
    def __init__(self, type: int, m: int, parameters: List[Cell], n: int, elements: List[Cell]):
        self.type = type
        self.m = m
        self.parameters = parameters
        self.n = n
        self.elements = elements

    def children(self):
        return self.parameters + self.elements


class Function(RuntimeObject):
    def __init__(self, closure, n: int, parameters: List[Cell]):
        self.closure = closure
        self.n = n
        self.parameters = parameters

    def children(self):
        return self.parameters


class Indirection(RuntimeObject):
    def __init__(self, obj: Cell):
        self.object = obj

    def children(self):
        return (self.object,)


class Id(RuntimeObject):
    def __init__(self, id: int):
        self.id = id