import logging
import asyncio

from level import LevelStorage
from kademlia.network import Server
from kademlia.storage import ForgetfulStorage

class New():
    def __init__(self, port):
        loop = asyncio.get_event_loop()
        loop.set_debug(True)

        server = Server()
        loop.run_until_complete(server.listen(port))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()
            loop.close()

class Logger():
    def __init__ (self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)
        

class NodeServer ():
    def __init__ (self, address : str, port : int, **kwargs):
        name = str(port)
        defaultstore = LevelStorage(name)
        # defaultstore = ForgetfulStorage()
        storage = kwargs.get('storage', defaultstore)
        bootstrap_nodes = kwargs.get('bootstrap', [])
        server = Server(storage=storage)
        self.port = port
        self.bootstrap_nodes = bootstrap_nodes 
        self.server = server

    async def start (self):
        await self.server.listen(self.port)
        # bootstrap_node = (self.node, int(self.port))
        if len(self.bootstrap_nodes) > 0 :
            await self.server.bootstrap(self.bootstrap_nodes)

    async def stop (self):
        await self.server.stop()
        
    async def get(self, key):
        result = await self.server.get(key)
        return result

    async def put (self, key, value):
        await self.server.set(key, value)
        return (key, value)

class Node(NodeServer):
    def __init__ (self, address : str, port : int, **kwargs):
        NodeServer.__init__(self, address, port, **kwargs)
        self.address = address
        self.port = port

    # async def get(self, key):
    #     await NodeServer.start(self) 
    #     result = await self.server.get(key)
    #     return result

    # async def put (self, key, value):
    #     await NodeServer.start(self) 
    #     await self.server.set(key, value)
    #     return (key, value)