#https://github.com/bmuller/kademlia/blob/9075feb3f69ad2bc48ee8af39101666a4dac82e8/kademlia/storage.py

import os
import shelve
from contextlib import closing, contextmanager
from threading import Lock

from _gdbm import error as shelve_error

from kademlia.utils import retry

from kademlia.storage import IStorage

class DiskStorage(IStorage):
    def __init__(self, filename=None):
        self.filename = os.path.realpath('kademlia.db')
        if filename:
            self.filename = os.path.realpath(filename)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        self.lock = Lock()

    # pylint: disable=no-self-use
    def _key(self, key):
        if isinstance(key, bytes):
            return key.hex()
        return key

    @contextmanager
    def database(self):
        with self.lock:
            with closing(shelve.open(self.filename)) as database:
                yield database

    @retry(shelve_error)
    def __setitem__(self, key, item):
        with self.database() as database:
            # pylint: disable=unsupported-assignment-operation
            database[self._key(key)] = (time.monotonic(), item)

    @retry(shelve_error)
    def __getitem__(self, key):
        with self.database() as database:
            # pylint: disable=unsubscriptable-object
            result = database[self._key(key)][1]
        return result

    @retry(shelve_error)
    def get(self, key, default=None):
        with self.database() as database:
            result = default
            # pylint: disable=unsupported-membership-test
            if self._key(key) in database:
                # pylint: disable=unsubscriptable-object
                result = database[self._key(key)][1]
        return result

    @retry(shelve_error)
    def __delitem__(self, key):
        with self.database() as database:
            # pylint: disable=unsupported-delete-operation
            del database[self._key(key)]

    @retry(shelve_error)
    def __contains__(self, item):
        with self.database() as database:
            # pylint: disable=unsupported-membership-test
            result = item in database
        return result

    @retry(shelve_error)
    def __iter__(self):
        with self.database() as database:
            # pylint: disable=no-member
            for k in database.keys():
                # pylint: disable=unsubscriptable-object
                yield (k, database[k][1])

    @retry(shelve_error)
    def iter_older_than(self, seconds_old):
        with self.database() as database:
            min_birthday = time.monotonic() - seconds_old
            zipped = self._triple_iter(database)
            matches = takewhile(lambda r: min_birthday >= r[1], zipped)
            result = list(map(operator.itemgetter(0, 2), matches))
        return result

    def _triple_iter(self, database):
        ikeys = list(database.keys())
        ibirthday = map(operator.itemgetter(0), database.values())
        ivalues = map(operator.itemgetter(1), database.values())
        return zip(ikeys, ibirthday, ivalues)