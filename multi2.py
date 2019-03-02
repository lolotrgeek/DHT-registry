import asyncio

from dht import Logger
from dht import Node

Logger()

node = Node('127.0.0.1', 8467, bootstrap=[('127.0.0.1', 8468)])

async def main():
    get = await node.get('key1')
    print('GET: ', get)

loop = asyncio.get_event_loop()
loop.set_debug(True)

loop.run_until_complete(node.start())

# loop.run_until_complete(main())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()