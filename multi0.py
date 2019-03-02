import asyncio

from dht import Logger
from dht import Node

Logger()

node0 = Node('127.0.0.1', 8469)

# async def main():
#     put = await node0.put('key', 'value')
#     print('PUT: ', put)

loop = asyncio.get_event_loop()
loop.set_debug(True)

loop.run_until_complete(node0.start())

# loop.run_until_complete(main())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()