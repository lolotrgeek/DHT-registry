import random
import logging
import asyncio
import pickle
import utils

from level import LevelStorage
from kademlia.network import Server
from kademlia.utils import digest

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)

class Logger():
    def __init__ (self):
        self.log = log
        self.log.setLevel(logging.DEBUG)

class NodeServer(Server):
    def __init__ (self, ksize=20, alpha=3, node_id=None, storage=None, **kwargs):
        name = node_id or digest(random.getrandbits(255))
        long_id = str(int(name.hex(), 16))
        self.name = name
        self.long_id = long_id
        super().__init__(ksize=20, alpha=3, node_id=name, storage=storage)


    async def load_state(self, fname):
        """
        Load the state of this node (the alpha/ksize/id/immediate neighbors)
        from a cache file with the given fname.
        """
        log.info("Loading state from %s", fname)
        with open(fname, 'rb') as file:
            data = pickle.load(file)

        return (data['ksize'], data['alpha'], data['id'], data['neighbors'])

    def save_state(self, fname):
        """
        Save the state of this node (the alpha/ksize/id/immediate neighbors)
        to a cache file with the given fname.
        """
        log.info("Saving state to %s", fname)
        data = {
            'ksize': self.ksize,
            'alpha': self.alpha,
            'id': self.node.id,
            'neighbors': self.bootstrappable_neighbors()
        }
        # print('STATE: ', data)
        log.info("Neighbors: %s", data['neighbors'])
        with open(fname, 'wb') as file:
            pickle.dump(data, file)


class Node ():
    def __init__ (self, address : str, port : int, **kwargs):
        defaultnodes = []
        self.logging = kwargs.get('logging', True)
        self.address = address
        self.port = port
        self.bootstrap_nodes = kwargs.get('bootstrap', defaultnodes)
        self.server = NodeServer()
        self.node_id = self.server.name
        self.fname = 'state'+str(port)


    async def start (self):
        if self.logging == True:
            Logger()
        try:
            state = await self.server.load_state(self.fname)
            # log.info(state)
            log.info("Updating Server '%s'", self.server)
            storage = LevelStorage(str(int(state[2].hex(), 16)))
            self.server = NodeServer(ksize=state[0], alpha=state[1], node_id=state[2])
            await self.server.listen(self.port, self.address)
            self.server.save_state(self.fname)
            # log.info(state[3])
            await self.server.bootstrap(state[3])
        except :
            try :
                log.info("Creating New Server '%s'", self.server)
                storage = LevelStorage(self.server.long_id)
                self.server = NodeServer(node_id=self.node_id, storage=storage)
                await self.server.listen(self.port, self.address)
                self.server.save_state(self.fname)
                if len(self.bootstrap_nodes) > 0 :
                    await self.server.bootstrap(self.bootstrap_nodes)
            except : 
                utils.removeDB(self.node_id)
        finally :
            self.server.save_state_regularly(self.fname, frequency=10)


    def stop (self):
        self.server.save_state(self.fname)
        self.server.stop()
        
    async def get(self, key):
        result = await self.server.get(key)
        self.server.save_state(self.fname)
        return result

    async def put (self, key, value):
        await self.server.set(key, value)
        self.server.save_state(self.fname)
        return (key, value)
