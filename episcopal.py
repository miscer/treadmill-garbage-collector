import treadmill

heap = treadmill.Heap()

foo = heap.allocate()
bar = heap.allocate()
baz = heap.allocate()

bar.add_child(foo)
baz.add_child(foo)

print(heap.objects)
