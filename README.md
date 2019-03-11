DHT Registry with LevelDB key/value store.

a few things to note: 

a node's state is a tuple of it's `alpha` / `ksize` / `id` / `immediate neighbors`
each node's state is saved using a dataframe file named `state` plus it's port number
the key/value store for a node is placed in a folder named by it's port number

## Install
requires python 3.5 or greater
```
$ pip install kademlia
$ pip install pylyvel
```

## Usage
clone this repo, go to directory

run `python server.py`
run `python client.py`


## TODO
Create flatter design, all servers are clients and all clients are servers