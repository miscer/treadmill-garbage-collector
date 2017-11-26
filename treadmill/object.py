class Object:
    def __init__(self, mark, previous, next):
        self.mark = mark
        self.previous = previous
        self.next = next
        self.children = []
        self.value = None

    def add_child(self, child: 'Object'):
        self.children.append(child)


def initialize_objects(size, mark):
    first = last = Object(mark=mark, previous=None, next=None)

    for _ in range(1, size):
        interim = Object(mark=mark, previous=last, next=None)
        last.next = interim
        last = interim

    last.next = first
    first.previous = last

    return first
