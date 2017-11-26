from treadmill import Cell
from treadmill.list import initialize, insert_after, iterate, insert_between, remove


def test_initialize():
    cell = Cell()
    initialize(cell)

    assert cell.next == cell
    assert cell.previous == cell


def test_insert_between_single():
    cell = Cell()
    initialize(cell)

    inserted = Cell()
    insert_between(inserted, cell, cell)

    assert cell.next == inserted
    assert cell.previous == inserted

    assert inserted.previous == cell
    assert inserted.next == cell


def test_insert_between_multiple():
    cell1, cell2, cell3 = Cell(), Cell(), Cell()

    initialize(cell1)
    insert_after(cell2, cell1)

    insert_between(cell3, cell1, cell2)

    assert cell1.next == cell3
    assert cell3.previous == cell1
    assert cell3.next == cell2
    assert cell2.previous == cell3


def test_iterate():
    cells = [Cell(), Cell(), Cell()]

    initialize(cells[0])
    insert_after(cells[1], cells[0])
    insert_after(cells[2], cells[1])

    assert list(iterate(cells[0])) == cells


def test_remove_one():
    cell = Cell()
    initialize(cell)

    remove(cell)

    assert cell.next is None
    assert cell.previous is None


def test_remove_two():
    cell1, cell2 = Cell(), Cell()

    initialize(cell1)
    insert_after(cell2, cell1)

    remove(cell1)

    assert cell2.next == cell2
    assert cell2.previous == cell2


def test_remove_three():
    cell1, cell2, cell3 = Cell(), Cell(), Cell()

    initialize(cell1)
    insert_after(cell2, cell1)
    insert_after(cell3, cell2)

    remove(cell2)

    assert cell1.next == cell3
    assert cell3.previous == cell1