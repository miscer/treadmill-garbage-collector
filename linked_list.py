from episcopal.garbage import get_children
from episcopal.runtime import Indirection
from treadmill import Heap


def heap_roots():
    return [episcopal_list] if episcopal_list else []


def heap_children(cell):
    global heap

    return get_children(heap.read(cell))


def list_init():
    global heap

    head = heap.allocate()
    heap.write(head, Indirection(None))
    return head


def list_add(head):
    global heap

    new_head = heap.allocate()
    heap.write(new_head, Indirection(head))
    return new_head


def create_list():
    global episcopal_list

    episcopal_list = list_init()

    for _ in range(100):
        episcopal_list = list_add(episcopal_list)


heap = Heap(heap_roots, heap_children, initial_size=10, scan_step_size=5)
print(heap.string())

for _ in range(10):
    episcopal_list = None
    create_list()

    print(heap.string())
