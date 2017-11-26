def initialize(obj):
    assert obj.next is None
    assert obj.previous is None

    obj.next = obj
    obj.previous = obj


def insert_before(obj, right):
    left = right.previous
    insert_between(obj, left, right)


def insert_after(obj, left):
    right = left.next
    insert_between(obj, left, right)


def insert_between(obj, left, right):
    assert left.next == right
    assert right.previous == left

    left.next = obj
    right.previous = obj

    obj.previous = left
    obj.next = right


def remove(obj):
    left = obj.previous
    right = obj.next

    left.next = right
    right.previous = left

    obj.next = None
    obj.previous = None


def iterate(obj):
    first = obj

    while True:
        yield obj

        obj = obj.next

        if obj == first:
            break
