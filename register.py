import asyncio
from dht import Node


class main():
    def __init__(self, ip, port): 
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        self.node = Node(ip, port)
        loop.run_until_complete(self.node.start())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.node.stop()
            loop.close()

    async def get(self, key) :
        await self.node.get(key)

    async def put(self, key, value):
        await self.node.put(key, value)
