import asyncio
import sys

from dht import New
from dht import Logger
from dht import Node

from threading import Thread

Logger()

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

set_loop = asyncio.new_event_loop()
get_loop = asyncio.new_event_loop()


ts = Thread(target=start_background_loop, args=(set_loop,))
ts.start()

tg = Thread(target=start_background_loop, args=(get_loop,))
tg.start()

setwork = asyncio.run_coroutine_threadsafe(
    Node('127.0.0.1', 8468).put('mykey', 'myval'),
    set_loop
)

getwork = asyncio.run_coroutine_threadsafe(
    Node('127.0.0.1', 8468).get('mykey'),
    get_loop
)


print(setwork.result())
print(getwork.result())