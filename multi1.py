import asyncio

from dht import Node

node = Node('127.0.0.1', 8468)

async def main():
    put = await node.put('key1', 'value1')
    print('PUT: ', put)

loop = asyncio.get_event_loop()
loop.set_debug(True)

loop.run_until_complete(node.start())

loop.run_until_complete(main())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()