from typing import Callable, Iterable

from treadmill.list import remove, insert_after, initialize, insert_before
from treadmill.cell import Cell

GetRootsFn = Callable[[], Iterable[Cell]]
GetChildrenFn = Callable[[Cell], Iterable[Cell]]


def create_free_cells(size):
    first = Cell()
    initialize(first)

    for _ in range(size - 1):
        insert_before(Cell(), first)

    return first


class Heap:
    def __init__(self,
                 get_roots: GetRootsFn,
                 get_children: GetChildrenFn,
                 initial_size: int = 30,
                 scan_step_size: int = 5,
                 expand_size: int = 10,
                 scan_threshold: float = 0.2):
        self.get_roots = get_roots
        self.get_children = get_children
        self.scan_step_size = scan_step_size
        self.expand_size = expand_size
        self.scan_threshold = scan_threshold

        self.live_mark = True

        # used to know when there is not enough memory left
        self.num_free = initial_size
        self.num_total = initial_size
        self.num_scanned = 0

        self.free = create_free_cells(initial_size)
        self.top = self.bottom = self.scan = None

    def allocate(self) -> Cell:
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
        cell = self.free
        self.free = self.free.next

        # update number of free cells
        self.num_free -= 1

        # mark the cell
        cell.mark = self.live_mark

        # initialise the bottom pointer
        if self.bottom is None:
            self.bottom = cell

        return cell

    def read(self, cell):
        print('Read', cell)

        if self.is_scanning():
            # if scanning, the cell needs to be grey or black before read
            self.mark_to_scan(cell)

        return cell.value

    def write(self, cell, value):
        print('Write', cell, value)
        cell.value = value

    def needs_collecting(self):
        return (self.num_free / self.num_total) <= self.scan_threshold

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

        self.num_scanned = 0
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
            self.bottom = None  # TODO: don't remove bottom?
            self.num_free = self.num_total

    def scan_cycle(self):
        print('Scan cycle')

        for _ in range(self.scan_step_size):
            continue_scan = self.scan_step()

            if not continue_scan:
                break

    def scan_step(self):
        print('Scan step', self.scan)

        assert self.scan is not None
        assert self.bottom is not None

        # mark all children to be scanned
        for child in self.get_children(self.scan):
            self.mark_to_scan(child)

        self.num_scanned += 1

        if self.top is not None and self.scan.previous == self.top:
            print('Stop and collect garbage')
            # all grey cells were scanned, so we can stop and collect garbage
            self.scan = None
            self.collect()
            return False

        elif self.scan == self.bottom:
            print('No garbage')
            # there are no white cells left, i.e. there is no garbage
            self.scan = None
            self.start_scanning()
            return False

        else:
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

        # update statistics
        self.num_free = self.num_total - self.num_scanned

    def mark_to_scan(self, cell):
        print('Mark to scan', cell)

        assert self.bottom is not None

        if cell.mark == self.live_mark:
            print('Cell is already grey or black')
            # do nothing if the cell is already grey or black
            return

        assert self.top is not None

        # mark the cell as live
        cell.mark = self.live_mark

        if cell == self.bottom and cell == self.top:
            print('Marking the only white cell grey')
            # marking the only white cell grey
            # no manipulation needed, just update the top pointer
            self.top = None
        elif cell == self.bottom:
            print('Marking the last white cell grey')
            # marking the last white cell grey
            # update the bottom pointer to the next white cell
            self.bottom = cell.next

            # remove the cell from whites and add it to greys
            remove(cell)
            insert_after(cell, self.top)
        elif cell == self.top:
            print('Marking the first white cell grey')
            # marking the first white cell grey
            # no manipulation needed, just update the top pointer
            self.top = cell.previous
        else:
            print('Cell is neither the first or last white cell')
            # cell is neither the first or last white cell
            # move the cell from whites to greys
            remove(cell)
            insert_after(cell, self.top)

    def expand(self):
        print('Expand')

        # assert that there is only one free cell
        assert self.free.next == self.bottom

        first_extra = create_free_cells(self.expand_size)
        last_extra = first_extra.previous

        self.free.next = first_extra
        self.bottom.previous = last_extra

        first_extra.previous = self.free
        last_extra.next = self.bottom

        self.num_total += self.expand_size
        self.num_free += self.expand_size

    def string(self):
        return '{} free out of {} total, {} scanned'.format(self.num_free, self.num_total,
                                                            self.num_scanned)
