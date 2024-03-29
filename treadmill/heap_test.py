from treadmill.heap import create_free_cells, Heap
from treadmill.list import iterate


def dummy_get_roots():
    return ()


def dummy_get_children(obj):
    return ()


def test_create_free_cells():
    first = create_free_cells(10)
    assert len(list(iterate(first))) == 10


def test_first_allocation():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    cells = list(heap.free)
    allocated = heap.allocate()

    assert allocated == cells[0]
    assert heap.free == cells[1]
    assert heap.bottom == cells[0]
    assert heap.num_free == 9
    assert allocated.mark == heap.live_mark


def test_allocate_starting_collection_and_collecting():
    def get_roots():
        return cells[0:3]

    heap = Heap(get_roots=get_roots,
                get_children=dummy_get_children,
                initial_size=10,
                scan_threshold=0.5,
                scan_step_size=2)

    cells = list(heap.free)

    # cells 7-9 are free, cells 0-2 are roots, cells 3-6 are potential garbage
    heap.free = cells[7]
    heap.bottom = cells[0]
    heap.num_free = 2

    allocated = heap.allocate()

    # cell 7 is allocated, cells 0-1 were scanned, cell 2 is yet to be scanned, cells 3-6 are
    # potential garbage, cells 8-9 are free
    assert allocated == cells[7]
    assert heap.free == cells[8]
    assert heap.scan == cells[2]
    assert heap.bottom == cells[3]
    assert heap.top == cells[6]

    assert cells[0].mark == heap.live_mark
    assert cells[1].mark == heap.live_mark
    assert cells[2].mark == heap.live_mark


def test_allocate_expands():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10,
                scan_threshold=0.001,
                expand_size=10)

    cells_before = list(heap.free)

    # cell 9 is free, others are used
    heap.free = cells_before[9]
    heap.bottom = cells_before[0]
    heap.num_free = 1

    allocated = heap.allocate()
    cells_after = list(heap.bottom)

    # cell 9 is allocated, 10-19 are free
    assert allocated == cells_before[9]
    assert heap.free == cells_after[10]
    assert heap.bottom == cells_before[0]
    assert heap.num_free == 10
    assert heap.num_total == 20


def test_allocate_expands_with_one_initial_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=1,
                expand_size=10)

    cells_before = list(heap.free)
    allocated = heap.allocate()
    cells_after = list(heap.free)

    assert len(cells_before) == 1
    assert len(cells_after) == 11


def test_read_unscanned_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    cells = list(heap.free)

    # cells 7-9 are free, cells 4-6 are marked to be scanned, cells 0-3 are yet to be scanned
    heap.free = cells[7]
    heap.scan = cells[6]
    heap.top = cells[3]
    heap.bottom = cells[0]

    cells[4].mark = cells[5].mark = cells[6].mark = heap.live_mark

    # cell 2 is yet to be scanned and has a value
    cells[2].value = 123

    value = heap.read(cells[2])

    assert value == 123
    assert cells[2].mark == heap.live_mark
    assert list(heap.bottom) == cells[0:2] + [cells[3], cells[2]] + cells[4:]


def test_write():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=1)

    cell = heap.free
    heap.write(cell, 123)

    assert cell.value == 123


def test_start_scanning_without_live_cells():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    # no live cells
    heap.start_scanning()

    # all cells are still free, nothing changed
    assert heap.scan is None
    assert heap.bottom is None
    assert heap.top is None


def test_start_scanning_without_any_roots():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    cells = list(heap.free)

    # cells 7-9 are free, 0-6 are about to be scanned, no roots
    heap.free = cells[7]
    heap.bottom = cells[0]

    heap.start_scanning()

    # all cells are free
    assert heap.scan is None
    assert heap.bottom is None
    assert heap.top is None

    assert heap.num_free == 10


def test_start_scanning_with_roots():
    def get_roots():
        return [cells[2], cells[3]]

    heap = Heap(get_roots=get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    cells = list(heap.free)

    # cells 7-9 are free, 0-6 are about to be scanned, 2-3 are roots
    heap.free = cells[7]
    heap.bottom = cells[0]

    heap.start_scanning()

    assert heap.scan == cells[2]
    assert heap.bottom == cells[0]
    assert heap.top == cells[6]

    assert cells[2].mark == heap.live_mark
    assert cells[3].mark == heap.live_mark

    assert list(heap.free) == (cells[7:] + cells[:2] + cells[4:7] + [cells[3], cells[2]])


def test_scan_cycle():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10,
                scan_step_size=5)

    cells = list(heap.free)

    # cells 7-9 are free, cells 4-6 are marked to be scanned, cells 0-3 are garbage
    heap.free = cells[7]
    heap.scan = cells[6]
    heap.bottom = cells[0]
    heap.top = cells[3]

    heap.num_free = 3

    cells[4].mark = cells[5].mark = cells[6].mark = heap.live_mark

    assert heap.num_scanned == 0

    heap.scan_cycle()

    # cells 7-9 and 0-3 are free, cells 4-6 are live
    assert heap.free == cells[7]
    assert heap.scan is None
    assert heap.bottom == cells[4]
    assert heap.top is None

    assert heap.num_free == 7
    assert heap.num_scanned == 3


def test_scan_step_marks_all_children():
    def get_children(obj):
        return [cells[0], cells[1]]

    heap = Heap(get_roots=dummy_get_roots,
                get_children=get_children,
                initial_size=4)

    cells = list(heap.free)

    heap.free = cells[3]
    heap.scan = cells[2]
    heap.top = cells[1]
    heap.bottom = cells[0]

    cells[2].mark = heap.live_mark

    assert cells[0].mark != heap.live_mark
    assert cells[1].mark != heap.live_mark

    assert heap.num_scanned == 0

    continue_scan = heap.scan_step()

    assert continue_scan

    assert list(heap.free) == [cells[3], cells[1], cells[0], cells[2]]

    assert heap.scan == cells[0]
    assert heap.top is None
    assert heap.bottom == cells[1]

    assert cells[0].mark == heap.live_mark
    assert cells[1].mark == heap.live_mark

    assert heap.num_scanned == 1


def test_scan_step_stops_and_collects():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    cells = list(heap.free)

    # cells 7-9 are free, cells 4-6 are live, cells 0-3 are garbage
    heap.free = cells[7]
    heap.scan = cells[4]
    heap.top = cells[3]
    heap.bottom = cells[0]

    heap.num_free = 3
    heap.num_scanned = 3

    continue_scan = heap.scan_step()
    assert not continue_scan

    # cells 7-9 and 0-3 are free, cells 4-6 are live
    assert heap.free == cells[7]
    assert heap.scan is None
    assert heap.top is None
    assert heap.bottom == cells[4]

    assert heap.num_free == 6


def test_scan_step_restarts_if_no_garbage():
    def get_roots():
        return [cells[6]]

    heap = Heap(get_roots=get_roots,
                get_children=dummy_get_children,
                initial_size=10)

    cells = list(heap.free)

    # cells 7-9 are free, cells 0-6 are live, no garbage
    heap.free = cells[7]
    heap.scan = cells[0]
    heap.top = None
    heap.bottom = cells[0]

    heap.num_free = 3
    heap.num_scanned = 7

    continue_scan = heap.scan_step()
    assert not continue_scan

    # cells 7-9 are free, cells 0-6 are live, scan is restarted
    assert heap.free == cells[7]
    assert heap.scan == cells[6]
    assert heap.top == cells[5]
    assert heap.bottom == cells[0]

    assert heap.num_scanned == 0


def test_collect():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=5)

    cells = list(heap.free)

    # cells 3-4 are free, 2 is live, 0-1 are garbage
    heap.free = cells[3]
    heap.bottom = cells[0]
    heap.top = cells[1]

    heap.num_free = 2
    heap.num_scanned = 1

    heap.collect()

    # cells 3-4 and 0-1 are free, 2 is live
    assert heap.free == cells[3]
    assert heap.bottom == cells[2]
    assert heap.top is None


def test_mark_to_scan_scanned_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=3)

    first, second, third = heap.free

    heap.free = third
    heap.bottom = first
    heap.top = first

    second.mark = heap.live_mark

    heap.mark_to_scan(second)

    # nothing has changed
    assert heap.free == third
    assert heap.bottom == first
    assert heap.top == first

    assert second.mark == heap.live_mark


def test_mark_to_scan_the_only_white_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=3)

    first, second, third = heap.free

    heap.free = third
    heap.bottom = first
    heap.top = first

    heap.mark_to_scan(first)

    assert heap.free == third
    assert heap.bottom == first
    assert heap.top is None

    assert first.mark == heap.live_mark

    assert list(first) == [first, second, third]


def test_mark_to_scan_first_white_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=3)

    first, second, third = heap.free

    heap.free = third
    heap.bottom = first
    heap.top = second

    heap.mark_to_scan(second)

    assert heap.free == third
    assert heap.bottom == first
    assert heap.top == first

    assert second.mark == heap.live_mark

    assert list(first) == [first, second, third]


def test_mark_to_scan_last_white_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=3)

    first, second, third = heap.free

    heap.free = third
    heap.bottom = first
    heap.top = second

    heap.mark_to_scan(first)

    assert heap.free == third
    assert heap.bottom == second
    assert heap.top == second

    assert first.mark == heap.live_mark

    assert list(second) == [second, first, third]


def test_mark_to_scan_middle_cell():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=4)

    first, second, third, fourth = heap.free

    heap.free = fourth
    heap.bottom = first
    heap.top = third

    heap.mark_to_scan(second)

    assert heap.free == fourth
    assert heap.bottom == first
    assert heap.top == third

    assert second.mark == heap.live_mark

    assert list(first) == [first, third, second, fourth]


def test_expand():
    heap = Heap(get_roots=dummy_get_roots,
                get_children=dummy_get_children,
                initial_size=5,
                expand_size=10)

    first_cell = heap.free
    cells = list(first_cell)

    # 4 cells allocated (index 0-3), 1 free (index 4)
    heap.free = cells[4]
    heap.bottom = cells[0]
    heap.num_free = 1

    assert heap.num_total == 5

    heap.expand()
    assert heap.num_total == 15
    assert heap.num_free == 11

    cells = list(first_cell)

    assert len(cells) == 15
    assert heap.free == cells[4]
    assert heap.bottom == cells[0]