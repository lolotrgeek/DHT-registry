import asyncio

from dht import New
from dht import Logger
from dht import Node


Logger()

async def main():
    put = await node.put('mykey', 'myval')
    print(put)
    get = await node.get('mykey')
    print(get)

node = Node('127.0.0.1', 8468)
asyncio.run(main())