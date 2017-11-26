from treadmill.heap import create_free_cells, Heap, INITIAL_SIZE
from treadmill.list import iterate


def dummy_get_roots():
    return ()


def dummy_get_children():
    return ()


def test_create_free_cells():
    first = create_free_cells(10)
    assert len(list(iterate(first))) == 10
