from treadmill.list import iterate


class Cell:
    def __init__(self):
        self.mark = None
        self.previous = None
        self.next = None
        self.value = None

    def __iter__(self):
        return iterate(self)