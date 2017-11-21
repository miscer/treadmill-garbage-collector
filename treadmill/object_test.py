from treadmill.object import initialize_objects


def test_creating_circular_links():
    first = initialize_objects(3, 0)
    second = first.next
    third = second.next

    assert first != second
    assert second != third
    assert third != first

    assert second.previous == first
    assert third.previous == second
    assert first.previous == third
    assert third.next == first

    assert first.mark == 0


def test_creating_list_with_single_element():
    first = initialize_objects(1, 0)
    assert first.next == first
    assert first.previous == first