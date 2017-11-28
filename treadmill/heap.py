import logging
from typing import Callable, Iterable

from treadmill.list import remove, insert_after, initialize, insert_before
from treadmill.cell import Cell

GetRootsFn = Callable[[], Iterable[Cell]]
GetChildrenFn = Callable[[Cell], Iterable[Cell]]

log = logging.getLogger('episcopal')


def create_free_cells(size):
    """
    Creates a list containing the specified number of free cells. Returns the
    first cell.
    """
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

    def allocate(self):
        """
        Allocates a new cell and returns it. Continues or starts scanning if
        needed, or expands the heap if there are no free cells left.
        """
        log.debug('Allocate')

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
        """
        Returns the value stored in the cell. Automatically marks the cell as
        live.
        """
        log.debug('Read %s', cell)

        if self.is_scanning():
            # if scanning, the cell needs to be grey or black before read
            self.mark_to_scan(cell)

        return cell.value

    def write(self, cell, value):
        """
        Writes the value to the cell.
        """
        log.debug('Write %s to %s', value, cell)
        cell.value = value

    def needs_collecting(self):
        """
        Checks if the ratio of free and all cells is past the scan threshold
        and scanning should start.
        """
        return (self.num_free / self.num_total) <= self.scan_threshold

    def is_scanning(self):
        """
        Checks if scanning is currently in progress.
        """
        return self.scan is not None

    def is_full(self):
        """
        Checks if there is only one or no free cells.
        """
        return self.num_free <= 1

    def start_scanning(self):
        """
        Starts the scanning process by finind the roots and marking them to be
        scanned. If there are no roots, all cells are marked as free.
        """
        log.debug('Start scanning')

        assert self.top is None
        assert self.scan is None

        if self.bottom is None:
            # nothing to scan, there are no live cells
            log.debug('Nothing to scan')
            return

        self.num_scanned = 0
        self.live_mark = not self.live_mark

        # find the roots
        roots = list(self.get_roots())

        if roots:
            log.debug('Scanning %d roots', len(roots))

            # initialise the top pointer and paint all black cells white
            self.top = self.free.previous

            # if there are any roots, mark them to be scanned
            for root in roots:
                self.mark_to_scan(root)

            self.scan = roots[0]

        else:
            log.debug('No roots')
            # there are no roots, so all cells are now free
            self.top = None
            self.bottom = None
            self.num_free = self.num_total

    def scan_cycle(self):
        """
        Executes at most n scan steps, where n = scan_step_size.
        """
        log.debug('Scan cycle')

        for _ in range(self.scan_step_size):
            continue_scan = self.scan_step()

            if not continue_scan:
                break

    def scan_step(self):
        """
        Scans one cell by marking all its children to be scanned. If scanning
        finishes, collects the garbage. If no garbage is found, restarts
        scanning.
        """
        log.debug('Scan step %s', self.scan)

        assert self.scan is not None
        assert self.bottom is not None

        # mark all children to be scanned
        for child in self.get_children(self.scan):
            self.mark_to_scan(child)

        self.num_scanned += 1

        if self.top is not None and self.scan.previous == self.top:
            log.debug('Stop and collect garbage')
            # all grey cells were scanned, so we can stop and collect garbage
            self.scan = None
            self.collect()
            return False

        elif self.scan == self.bottom:
            log.debug('No garbage')
            # there are no white cells left, i.e. there is no garbage
            self.scan = None
            self.start_scanning()
            return False

        else:
            log.debug('Scanned')
            self.scan = self.scan.previous
            return True

    def collect(self):
        """
        Collects garbage when scanning is finished.
        """
        log.debug('Collect')

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
        """
        Marks cell to be scanned, if it isn't already and if it has not been
        scanned yet.
        """
        log.debug('Mark to scan %s', cell)

        assert self.bottom is not None

        if cell.mark == self.live_mark:
            log.debug('Cell is already grey or black')
            # do nothing if the cell is already grey or black
            return

        assert self.top is not None

        # mark the cell as live
        cell.mark = self.live_mark

        if cell == self.bottom and cell == self.top:
            log.debug('Marking the only white cell grey')
            # marking the only white cell grey
            # no manipulation needed, just update the top pointer
            self.top = None
        elif cell == self.bottom:
            log.debug('Marking the last white cell grey')
            # marking the last white cell grey
            # update the bottom pointer to the next white cell
            self.bottom = cell.next

            # remove the cell from whites and add it to greys
            remove(cell)
            insert_after(cell, self.top)
        elif cell == self.top:
            log.debug('Marking the first white cell grey')
            # marking the first white cell grey
            # no manipulation needed, just update the top pointer
            self.top = cell.previous
        else:
            log.debug('Cell is neither the first or last white cell')
            # cell is neither the first or last white cell
            # move the cell from whites to greys
            remove(cell)
            insert_after(cell, self.top)

    def expand(self):
        """
        Creates n free cells and adds them to the heap, where n = expand_size.
        """
        log.debug('Expand')

        first_extra = create_free_cells(self.expand_size)
        last_extra = first_extra.previous

        # insert the new cells into the list, after the current free cell
        left = self.free
        right = left.next

        left.next = first_extra
        first_extra.previous = left

        right.previous = last_extra
        last_extra.next = right

        self.num_total += self.expand_size
        self.num_free += self.expand_size

    def string(self):
        """
        Returns statistics formatted as a string
        """
        return '{} free out of {} total, {} scanned'.format(self.num_free, self.num_total,
                                                            self.num_scanned)
