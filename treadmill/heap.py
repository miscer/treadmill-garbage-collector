from typing import Callable, Set

from treadmill.object import Object


MAX_SIZE = 3


class Heap:
    def __init__(self, get_roots: Callable[[], Set[Object]]):
        self.get_roots = get_roots
        self.from_space = set()
        self.to_space = set()

    def allocate(self) -> Object:
        if len(self.to_space) == MAX_SIZE:
            self.collect()

        if len(self.to_space) < MAX_SIZE:
            obj = Object()
            self.to_space.add(obj)
            return obj
        else:
            raise Exception('Out of memory')

    def collect(self):
        print('Collecting!')

        self.from_space = self.to_space
        self.to_space = set()

        roots = self.get_roots()

        for root in roots:
            self.copy(root)

    def copy(self, obj):
        print('Copying {}'.format(obj))

        self.from_space.remove(obj)
        self.to_space.add(obj)

        for child in obj.children:
            self.copy(child)
