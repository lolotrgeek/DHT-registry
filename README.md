#DHT Registry with LevelDB key/value store.

a few things to note: 

- Nodes have a state defined by a tuple of `alpha` / `ksize` / `id` / `immediate neighbors`
- A Node's state is saved using a dataframe file named `state` plus it's port number
- Key/value store for a node is placed in a directory named using it's `id`

## Install
requires python 3.5 or greater
```
$ pip install kademlia
$ pip install pylyvel
```

## Usage
clone this repo, go to directory

run `python main.py`


## TODO
Create flatter design, all servers are clients and all clients are servers