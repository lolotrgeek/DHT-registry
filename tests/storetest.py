import time
from itertools import takewhile
import operator
from collections import OrderedDict

from kademlia.storage import IStorage

class StoreTest(IStorage):
    def __init__(self, ttl=604800):
        """
        By default, max age is a week.
        """
        self.data = OrderedDict()
        self.ttl = ttl

    def __setitem__(self, key, value):
        print(__name__, '- Key: ', key)
        if key in self.data:
            print(__name__, '- Key: ', key)
            del self.data[key]
        self.data[key] = (time.monotonic(), value)
        print(__name__, ' - SET: ', self.data[key])
        print(__name__, ' - DATA: ', self.data)
        self.cull()

    def cull(self):
        for _, _ in self.iter_older_than(self.ttl):
            print('Culling:' )
            self.data.popitem(last=False)

    def get(self, key, default=None):
        self.cull()
        print("Getting: ", key)
        if key in self.data:
            print('Found:', key)
            return self[key]
        return default

    def __getitem__(self, key):
        self.cull()
        print('GET:', self.data[key][1])
        return self.data[key][1]

    def __repr__(self):
        self.cull()
        print(__name__, ':', self.data)
        return repr(self.data)

    def iter_older_than(self, seconds_old):
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        print(__name__, ':', zipped)
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        print('Iterated Older Matches: ', matches)
        iterate = list(map(operator.itemgetter(0, 2), matches))
        print('Iterated Older Results:', iterate)
        return iterate

    def _triple_iter(self):
        ikeys = self.data.keys()
        ibirthday = map(operator.itemgetter(0), self.data.values())
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ibirthday, ivalues)

    def __iter__(self):
        self.cull()
        ikeys = self.data.keys()
        ivalues = map(operator.itemgetter(1), self.data.values())
        result = zip(ikeys, ivalues)
        print('Iterated Results:', result)
        return result
