import asyncio


from dht import Node


node = Node('127.0.0.1', 8468)

async def main():
    await node.start()
    put = await node.put('key', 'value')
    print('PUT: ', put)
    get = await node.get('key')
    print('GOT: ' , get)

asyncio.run(main())