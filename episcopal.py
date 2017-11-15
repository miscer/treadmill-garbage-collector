import treadmill

def get_roots():
    return roots

heap = treadmill.Heap(get_roots)

foo = heap.allocate()
bar = heap.allocate()
baz = heap.allocate()

print([foo, bar, baz])

roots = {bar}

bar.add_child(foo)

baz = heap.allocate()
print([foo, bar, baz])