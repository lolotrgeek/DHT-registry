import asyncio

from dht import Node

node0 = Node('127.0.0.1', 8469)

loop = asyncio.get_event_loop()
loop.set_debug(True)

loop.run_until_complete(node0.start())

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()