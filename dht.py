import logging
import asyncio

from level import LevelStorage
from kademlia.network import Server

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
    def __init__ (self, node, port, **kwargs):
        storage = kwargs.get('storage', LevelStorage())
        server = Server(storage=storage)
        self.node = node
        self.port = port
        self.server = server

    async def start (self, myport):
        await self.server.listen(myport)
        bootstrap_node = (self.node, int(self.port))
        await self.server.bootstrap([bootstrap_node])

    async def stop (self):
        await self.server.stop()

class Node(NodeServer):
    def __init__ (self, node, port):
        NodeServer.__init__(self, node, port)
        self.node = node
        self.port = port

    async def get(self, key):
        await NodeServer.start(self, 8469) 
        result = await self.server.get(key)
        return result

    async def put (self, key, value):
        await NodeServer.start(self, 8469) 
        await self.server.set(key, value)
        return (key, value)