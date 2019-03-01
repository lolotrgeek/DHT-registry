import asyncio

from dht import Logger
from dht import Node

Logger()

async def main():
    # put = await node.put('key', 'value')
    # print('PUT: ', put)
    get = await node.get('key')
    print('GOT: ' , get)


node = Node('127.0.0.1', 8468)
asyncio.run(main())