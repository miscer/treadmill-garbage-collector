def initialize(obj):
    """
    Initialises the passed element by creating a list containing just the
    element.
    """
    assert obj.next is None
    assert obj.previous is None

    obj.next = obj
    obj.previous = obj


def insert_before(obj, right):
    """
    Inserts obj before right, assuming that right is already in a list.
    """
    left = right.previous
    insert_between(obj, left, right)


def insert_after(obj, left):
    """
    Inserts obj after left, assuming that left is already in a list.
    """
    right = left.next
    insert_between(obj, left, right)


def insert_between(obj, left, right):
    """
    Inserts obj between left and right, assuming they are both in a list and
    next to each other.
    """
    assert left.next == right
    assert right.previous == left

    left.next = obj
    right.previous = obj

    obj.previous = left
    obj.next = right


def remove(obj):
    """
    Removes obj from its list.
    """
    left = obj.previous
    right = obj.next

    left.next = right
    right.previous = left

    obj.next = None
    obj.previous = None


def iterate(obj):
    """
    Yields all elements in the list, starting with obj.
    """
    first = obj

    while True:
        yield obj

        obj = obj.next

        if obj == first:
            break
