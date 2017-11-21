import treadmill

live_objects = []

def get_roots():
    return live_objects

heap = treadmill.Heap(get_roots)

for _ in range(2000):
    if len(live_objects) < 100:
        live_objects.append(heap.allocate())
        heap.print()
    else:
        live_objects.pop(0)

        live = heap.allocate()

        heap.print()

        if live in live_objects:
            print('Returned live object!')
            exit(1)

        live_objects.append(live)