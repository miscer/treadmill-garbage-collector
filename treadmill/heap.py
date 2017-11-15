from treadmill.object import Object


class Heap:
    def __init__(self):
        self.objects = set()

    def allocate(self) -> Object:
        obj = Object()
        self.objects.add(obj)
        return obj
