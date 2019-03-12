import utils
import level
import dht
import os
import utils
import asyncio
import unittest

from main import main

def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper
    
class TestPutGet(unittest.TestCase):
    @async_test
    async def test_localput (self):
        node = main('127.0.0.1', utils.getPort()) 
        await node.put('string', 'value')
        await node.put('dict', {'value' : 1})
        await node.put('tuple', ('value', 1))
        await node.put('list', ['value',1])

    @async_test
    async def test_localget (self):
        node = main('127.0.0.1', utils.getPort())
        await node.get('string')
        await node.get('dict')
        await node.get('tuple')
        await node.get('list')

    @async_test
    async def test_internalput (self):
        node = main(utils.getInternalAddress(), utils.getPort())
        await node.put('internal-string', 'value')
        await node.put('internal-dict', {'value' : 1})
        await node.put('internal-tuple', ('value', 1))
        await node.put('internal-list', ['value',1])
        self.assertTrue('success') 


    @async_test
    async def test_internalget (self):
        node = main(utils.getInternalAddress(), utils.getPort())
        await node.get('internal-string')
        await node.get('internal-dict')
        await node.get('internal-tuple')
        await node.get('internal-list')
        self.assertTrue('')

    @async_test
    async def test_externalput (self):
        node = main(utils.getPublicAddress(), utils.getPort()) 
        await node.put('external-string', 'value')
        await node.put('external-dict', {'value' : 1})
        await node.put('external-tuple', ('value', 1))
        await node.put('external-list', ['value',1])

    @async_test
    async def test_externalget (self):
        node = main(utils.getPublicAddress(), utils.getPort())
        await node.get('external-string')
        await node.get('external-dict')
        await node.get('external-tuple')
        await node.get('external-list')

if __name__ == '__main__':
    unittest.main()

# def testRunner():
#    while True:
#       newpid = os.fork()
#       if newpid == 0:
#         asyncio.run(localget())
#         asyncio.run(localget())
#         asyncio.run(internalput())
#         asyncio.run(internalget())
#         asyncio.run(externalput())
#         asyncio.run(externalget())
#       else:
#          pids = (os.getpid(), newpid)
#          print("parent: %d, child: %d\n" % pids)
#       reply = input("q for quit / c for new fork")
#       if reply == 'c': 
#           continue
#       else:
#           break

# testRunner()




# class TestSocketConnection(unittest.TestCase):
#     def setUp(self):
#         self.mock_server = MockServer("localhost", 1337)
#         self.socket_connection = SocketConnection("localhost", 1337)

#     @async_test
#     def test_sends_handshake_after_connect(self):
#         yield from self.socket_connection.connect()
#         self.assertTrue(self.mock_server.received_handshake())