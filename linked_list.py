from episcopal.garbage import get_children
from episcopal.runtime import Indirection
from treadmill import Heap


heap = None
episcopal_list = None


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


def create_list(size):
    global episcopal_list

    episcopal_list = list_init()

    for _ in range(size - 1):
        episcopal_list = list_add(episcopal_list)


if __name__ == '__main__':
    heap = Heap(heap_roots, heap_children, initial_size=10, scan_step_size=5)
    print(heap.string())

    for _ in range(10):
        episcopal_list = None
        create_list(100)

        print(heap.string())
