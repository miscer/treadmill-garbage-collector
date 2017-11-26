from treadmill.heap import create_free_cells, Heap
from treadmill.list import iterate


def dummy_get_roots():
    return ()


def dummy_get_children():
    return ()


def test_create_free_cells():
    first = create_free_cells(10)
    assert len(list(iterate(first))) == 10


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