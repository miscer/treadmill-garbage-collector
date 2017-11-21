from typing import Callable, Iterable

from treadmill.object import Object, initialize_objects

INITIAL_SIZE = 30
SCAN_STEP_SIZE = 2
EXPAND_SIZE = 5


def treadmill_remove(obj):
    left = obj.previous
    right = obj.next

    left.next = right
    right.previous = left

    obj.next = None
    obj.previous = None


def treadmill_insert_before(obj, right):
    left = right.previous
    treadmill_insert_between(obj, left, right)


def treadmill_insert_after(obj, left):
    right = left.next
    treadmill_insert_between(obj, left, right)


def treadmill_insert_between(obj, left, right):
    assert left.next == right
    assert right.previous == left

    left.next = obj
    right.previous = obj

    obj.previous = left
    obj.next = right


class Heap:
    def __init__(self, get_roots: Callable[[], Iterable[Object]]):
        self.get_roots = get_roots

        self.live_mark = True

        # used to know when there is not enough memory left
        self.num_free = INITIAL_SIZE

        self.free = initialize_objects(INITIAL_SIZE, None)
        self.top = self.bottom = self.scan = None

    def allocate(self) -> Object:
        print('Allocate')

        # check if we should start scanning
        if self.needs_collecting() and not self.is_scanning():
            self.start_scanning()

        # if scanning, scan a few pointers
        if self.is_scanning():
            self.scan_cycle()

        if self.is_full():
            self.expand()

        # mark the cell `free` points to black (i.e. allocated and used)
        obj = self.free
        self.free = self.free.next

        # mark the object
        obj.mark = self.live_mark

        # initialise the bottom pointer
        if self.bottom is None:
            self.bottom = obj

        return obj

    def needs_collecting(self):
        return True

    def is_scanning(self):
        return self.scan is not None

    def is_full(self):
        return self.free.next == self.bottom

    def start_scanning(self):
        print('Start scanning')

        assert self.top is None
        assert self.scan is None

        if self.bottom is None:
            # nothing to scan, there are no live cells
            print('Nothing to scan')
            return

        self.live_mark = not self.live_mark

        # find the roots
        roots = list(self.get_roots())

        if roots:
            print('Scanning', len(roots), 'roots')

            # initialise the top pointer and paint all black cells white
            self.top = self.free.previous

            # if there are any roots, mark them to be scanned
            for root in roots:
                self.mark_to_scan(root)

            self.scan = roots[0]

        else:
            print('No roots')
            # there are no roots, so all cells are now free
            self.top = None
            self.bottom = None # TODO: don't remove bottom?

    def scan_cycle(self):
        print('Scan cycle')

        for _ in range(SCAN_STEP_SIZE):
            continue_scan = self.scan_step()

            if not continue_scan:
                break

    def scan_step(self):
        print('Scan step', self.scan)

        assert self.scan is not None
        assert self.bottom is not None

        # mark all children to be scanned
        for child in self.scan.children:
            self.mark_to_scan(child)

        if self.top is not None and self.scan.previous == self.top:
            print('Stop and collect garbage')
            # all grey cells were scanned, so we can stop and collect garbage
            self.scan = None
            self.collect()
            return False

        if self.scan == self.bottom:
            print('No garbage')
            # there are no white cells left, i.e. there is no garbage
            self.scan = None
            self.start_scanning()
            return False

        print('Scanned')
        self.scan = self.scan.previous
        return True

    def collect(self):
        print('Collect')

        # assert that there are no grey cells, i.e. scanning is finished
        assert self.scan is None

        # assert that there are some white cells, i.e. there is garbage
        assert self.top is not None

        # set the bottom pointer to the last live cell
        self.bottom = self.top.next
        self.top = None

    def mark_to_scan(self, obj):
        print('Mark to scan', obj)

        assert self.bottom is not None

        if obj.mark == self.live_mark:
            print('Cell is already grey or black')
            # do nothing if the cell is already grey or black
            return

        assert self.top is not None

        if obj == self.bottom and obj == self.top:
            print('Marking the only white cell grey')
            # marking the only white cell grey
            # no manipulation needed, just update the top pointer
            self.top = None
        elif obj == self.bottom:
            print('Marking the last white cell grey')
            # marking the last white cell grey
            # update the bottom pointer to the next white cell
            self.bottom = obj.next

            # remove the cell from whites and add it to greys
            treadmill_remove(obj)
            treadmill_insert_after(obj, self.top)
        elif obj == self.top:
            print('Marking the first white cell grey')
            # marking the first white cell grey
            # no manipulation needed, just update the top pointer
            self.top = obj.previous
        else:
            print('Cell is neither the first or last white cell')
            # cell is neither the first or last white cell
            # move the cell from whites to greys
            treadmill_remove(obj)
            treadmill_insert_after(obj, self.top)

        # mark the cell as live
        obj.mark = self.live_mark

    def expand(self):
        print('Expand')

        # assert that there is only one free cell
        assert self.free.next == self.bottom

        first_extra = initialize_objects(EXPAND_SIZE, None)
        last_extra = first_extra.previous

        self.free.next = first_extra
        self.bottom.previous = last_extra

        first_extra.previous = self.free
        last_extra.next = self.bottom


    def print(self):
        current = self.free

        while True:
            print('O', end='')

            if current == self.bottom:
                print('B', end='')
            if current == self.top:
                print('T', end='')
            if current == self.scan:
                print('S', end='')
            if current == self.free:
                print('F', end='')

            current = current.next

            if current == self.free:
                break

        print()
