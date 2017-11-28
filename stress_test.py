import logging

import treadmill
from episcopal.garbage import get_children
from episcopal.runtime import Integer

logging.basicConfig(level=logging.DEBUG)

live_objects = []

def heap_roots():
    return live_objects

def heap_children(cell):
    return get_children(heap.read(cell))

heap = treadmill.Heap(heap_roots, heap_children)

def allocate():
    cell = heap.allocate()
    heap.write(cell, Integer(123))
    return cell

for _ in range(2000):
    if len(live_objects) < 100:
        live_objects.append(allocate())
    else:
        live_objects.pop(0)

        live = allocate()

        if live in live_objects:
            print('Returned live object!')
            exit(1)

        live_objects.append(live)

    print(heap.string())