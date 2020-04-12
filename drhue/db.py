class InMemory:
    def __init__(self):
        self.store = {}

    def insert(self, key, value):
        self.store[key] = value

    def read(self, key):
        return self.store[key]