import logging
import asyncio
import pickle

from level import LevelStorage
from kademlia.network import Server

class Logger():
    def __init__ (self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)
        self.log = log
        
class NodeServer(Server):
    def __init__ (self, ksize=20, alpha=3, node_id=None, storage=None, **kwargs):
        super().__init__(ksize=20, alpha=3, node_id=None, storage=None)

    async def load_state(self, fname):
        """
        Load the state of this node (the alpha/ksize/id/immediate neighbors)
        from a cache file with the given fname.
        """
        print("Loading state from %s", fname)
        with open(fname, 'rb') as file:
            data = pickle.load(file)

        return (data['ksize'], data['alpha'], data['id'], data['neighbors'])

class Node ():
    def __init__ (self, address : str, port : int, **kwargs):
        name = str(port)
        self.id = name 
        defaultlogger = Logger().log
        defaultstore = LevelStorage(self.id)
        log = kwargs.get('logger', defaultlogger)
        storage = kwargs.get('storage', defaultstore)
        bootstrap_nodes = kwargs.get('bootstrap', [])
        server = NodeServer(storage=storage)
        self.storage = storage
        self.address = address
        self.port = port
        self.bootstrap_nodes = bootstrap_nodes 
        self.server = server
        self.fname = 'state'+str(port)
        self.log = log


    async def start (self):
        try:
            state = await self.server.load_state(self.fname)
            self.id = state[2]
            # print(state)
            self.log.info("Updating Server '%s'", self.server)
            self.server = NodeServer(ksize=state[0], alpha=state[1], node_id=state[2], storage=self.storage)
            await self.server.listen(self.port, self.address)
            # print(state[3])
            await self.server.bootstrap(state[3])
        except :
            self.log.info('New state from kwargs')
            await self.server.listen(self.port, self.address)
            # bootstrap_node = (self.node, int(self.port))
            if len(self.bootstrap_nodes) > 0 :
                await self.server.bootstrap(self.bootstrap_nodes)

        finally :
            self.server.save_state(self.fname)
            self.server.save_state_regularly(self.fname, frequency=10)


    async def stop (self):
        await self.server.save_state(self.fname)
        await self.server.stop()
        
    async def get(self, key):
        result = await self.server.get(key)
        return result

    async def put (self, key, value):
        await self.server.set(key, value)
        return (key, value)
