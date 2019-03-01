import time
import binascii
import operator
import plyvel as level

from itertools import takewhile
from ast import literal_eval as make_tuple

from kademlia.storage import IStorage

class LevelStorage(IStorage):
    def __init__(self, ttl=604800):
        """
        By default, max age is a week.
        """
        db = level.DB('registry', create_if_missing=True)
        self.db = db
        self.data = None
        self.ttl = ttl

    def __setitem__(self, key, value):
        timestamp = str(time.monotonic())
        encodedtimevalue = str((timestamp, value)).encode('utf-8')
        self.db.put(key,encodedtimevalue)
        self.cull()

    def cull(self):
        for key in self.iter_older_than(self.ttl):
            self.db.delete(key)


    def get(self, key, default=None):
        ''' Gets (`timestamp`,`value`) tuple with a `default` if get fails'''
        self.cull()
        return self.db.get(key, default)

    def __getitem__(self, key):
        '''Gets only `value` from (`timestamp`,`value`) tuple'''
        self.cull()
        return self.db.get(key)[1]


    def iter_older_than(self, seconds_old):
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        '''TODO: this may need to be optimized into one db.iterator call'''
        ikeys = map(lambda item : self.decode_items(item[0]), self.db.iterator())
        ibirthday = map(lambda item : float(self.decode_items(item[1])[0]), self.db.iterator())
        ivalues = map(lambda item : self.decode_items(item[1])[1], self.db.iterator())
        return zip(ikeys, ibirthday, ivalues)

    def __iter__(self):
        '''TODO: this may need to be optimized into one db.iterator call'''
        self.cull()
        # data = self.db.iterator()
        # ikeys = data[0]
        # ivalues = data[1]
        # return zip(self.db.iterator())
        ikeys = map(lambda item : self.decode_items(item[0]), self.db.iterator())
        ivalues = map(lambda item : self.decode_items(item[1])[1], self.db.iterator())
        return zip(ikeys, ivalues)
    
    def decode_items(self, value):
        '''level db wants to store things as bytes this decodes them'''
        try: 
            val = value.decode('ascii')
            strtuple = val.find('(', 0, 1) # looks for `(` at index `1` of string
            if strtuple > -1 :
                return make_tuple(val)
            return val
        except:
            return value

    def dump(self):
        return zip(self.db.iterator())

    # def await_blocking(self, func):
    #     return self.loop.run_in_executor(None, func)