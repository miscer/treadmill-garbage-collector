class Object:
    def __init__(self):
        self.children = []

    def add_child(self, child: 'Object'):
        self.children.append(child)
