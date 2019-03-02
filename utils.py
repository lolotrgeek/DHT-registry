from collections import OrderedDict

import plyvel as level
from kademlia.routing import KBucket 
from level import LevelStorage

class storeOrdereredDict :
    def __init__(self, name, odict, storage):
        self.odict = odict
        self.storage = storage
        self.db = level.DB(name + 'KBucket', create_if_missing=True)

    def put(self): 
        storage.put()
        odict.keys()
        odict.values()