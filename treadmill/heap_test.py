from treadmill.heap import create_free_cells, Heap
from treadmill.list import iterate


def dummy_get_roots():
    return ()


def dummy_get_children():
    return ()


def test_create_free_cells():
    first = create_free_cells(10)
    assert len(list(iterate(first))) == 10


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