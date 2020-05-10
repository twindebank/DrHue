from __future__ import annotations

import time
from collections.abc import MutableMapping
from json import JSONDecodeError

import pickledb as pickledb
from loguru import logger

db = None


def _get_db():
    global db
    if db is None:
        db = pickledb.load('state.json', auto_dump=True)
    return db


FALSE = 'false'


class State(MutableMapping):
    def __init__(self, read_only=False):
        self.read_only = read_only
        self.db = _get_db()

    def __getitem__(self, key):
        val = self.db.get(key)
        if val is False:
            raise KeyError(key)
        if val is FALSE:
            return False
        return val

    def reload(self):
        """
        Reload the db from the file, try again if it fails (the file is probably being rewritten).
        """
        tries = [5, 5, 5, 5, 5]
        for i, t in enumerate(tries):
            try:
                self.db._loaddb()
            except JSONDecodeError:
                wait = t / 10
                logger.debug(f"Failed to reload dbt, waiting {wait:.2f}s and trying again.")
                time.sleep(wait)
                if i == len(tries) - 1:
                    raise RuntimeError("DB could not be reloaded.")

    def __setitem__(self, key, value):
        if self.read_only:
            raise TypeError("Can't set value for read only database.")
        if value is False:
            value = FALSE
        self.db.set(key, value)

    def __delitem__(self, key):
        self.db.rem(key)

    def __iter__(self):
        for key in self.db.getall():
            yield key

    def items(self):
        for key in self:
            yield key, self[key]

    def __len__(self):
        return len(self.db.getall())

    def setdefault(self, k: _KT, default: _VT = ...) -> _VT:
        try:
            self[k]
        except KeyError:
            self[k] = default


def get_obj_fqn(obj):
    return ".".join([obj.__module__, obj.__class__.__name__])
