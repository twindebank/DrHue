from __future__ import annotations

import json
from collections.abc import MutableMapping

from path import Path


class State(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self):
        self.file = Path('state.json')
        if self.file.exists():
            self.store = self.read_file()
        else:
            self.store = {}
            self.write_file()

    def read_file(self):
        return json.loads(self.file.read_text())

    def write_file(self):
        self.file.write_text(json.dumps(self.store))

    def __getitem__(self, key):
        self.store = self.read_file()
        return self.store[key]

    def __setitem__(self, key, value):
        if not isinstance(value, (bool, str, int, float)):
            raise ValueError("Must be simple immutable value.")
        self.store[key] = value
        self.write_file()

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def setdefault(self, k: _KT, default: _VT = ...) -> _VT:
        try:
            self[k]
        except KeyError:
            self[k] = default


def get_obj_fqn(obj):
    return ".".join([obj.__module__, obj.__class__.__name__])
