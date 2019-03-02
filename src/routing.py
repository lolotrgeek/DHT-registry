import heapq
import time
import operator
import asyncio

from itertools import chain
from collections import OrderedDict
from kademlia.utils import shared_prefix, bytes_to_bit_string, digest

import plyvel as level

class KBucket:
    def __init__(self, rangeLower, rangeUpper, ksize, name):
        self.db = level.DB(str(name)+'KBucket', create_if_missing=True)
        self.range = (rangeLower, rangeUpper)
        # self.nodes = list(self.db.iterator())
        self.replacement_nodes = OrderedDict()
        self.touch_last_updated()
        self.ksize = ksize

    def touch_last_updated(self):
        print('TOUCHING')
        self.last_updated = time.monotonic()

    def get_nodes(self):
        print('GETTING')
        nodes = list(map(lambda item : item, self.db.iterator()))
        print ('Get Nodes: ', nodes)
        return nodes

    def split(self):
        print('SPLITTING')
        midpoint = (self.range[0] + self.range[1]) / 2
        one = KBucket(self.range[0], midpoint, self.ksize)
        two = KBucket(midpoint + 1, self.range[1], self.ksize)
        nodes = chain(list(self.db.iterator()), self.replacement_nodes.values())
        for node in nodes:
            bucket = one if node.long_id <= midpoint else two
            bucket.add_node(node)

        return (one, two)

    def remove_node(self, node):
        print('REMOVING')
        if node.id in self.replacement_nodes:
            del self.replacement_nodes[node.id]
            print ('del node: ', node)

        if node.id in self.db.iterator():
            self.db.delete(node.id)
            print ('del node: ', node)

            if self.replacement_nodes:
                newnode_id, newnode = self.replacement_nodes.popitem()
                self.db.put(newnode_id, newnode)
                print ('del replacement node: ', node)

    def has_in_range(self, node):
        print('RANGING')
        return self.range[0] <= node.long_id <= self.range[1]

    def is_new_node(self, node):
        print('ISNEW')
        try : 
            self.db.get(node.id)
            return False
        except:
            return True

    def add_node(self, node):
        """
        Add a C{Node} to the C{KBucket}.  Return True if successful,
        False if the bucket is full.

        If the bucket is full, keep track of node in a replacement list,
        per section 4.1 of the paper.
        """
        # TRACING NODE creation
        # node :kadelmelia.node.Node
        #   node.id
        #   node.ip
        #   node.port
        #   node.long_id

        #key = node.id :bytes (SHA256) 
        #value = [node.id :int (hex16), address :string, port :int]
        print('ADD NODE:', node)
        for node in self.db.iterator():
            if node == node.id :
                self.db.delete(node)
                self.db.put(node.id, [node.long_id, node.ip, node.port])
                print ('add node: ', node, type( node))
            elif len(self) < self.ksize:
                self.db.put(node.id, [node.long_id, node.ip, node.port])
                print ('add node: ', node, type( node))
            else:
                if node.id in self.replacement_nodes:
                    del self.replacement_nodes[node.id]
                self.replacement_nodes[node.id] = node
                print ('add replacement node: ', node)

                return False
            return True

    def depth(self):
        print('DEPTH')
        vals = self.nodes
        sprefix = shared_prefix([bytes_to_bit_string(n.id) for n in vals])
        return len(sprefix)

    def head(self):
        print('HEAD')
        return list(self.nodes)[0]

    def __getitem__(self, node_id):
        print('GETTING')
        print(self.db.get(node_id, None))
        return self.db.get(node_id, None)

    def __len__(self):
        print('LENGTH')
        return len(self.nodes)


class TableTraverser:
    def __init__(self, table, startNode):
        index = table.get_bucket_for(startNode)
        table.buckets[index].touch_last_updated()
        self.current_nodes = table.buckets[index].get_nodes()
        self.left_buckets = table.buckets[:index]
        self.right_buckets = table.buckets[(index + 1):]
        self.left = True

    def __iter__(self):
        return self

    def __next__(self):
        """
        Pop an item from the left subtree, then right, then left, etc.
        """
        if self.current_nodes:
            return self.current_nodes.pop()

        if self.left and self.left_buckets:
            self.current_nodes = self.left_buckets.pop().get_nodes()
            self.left = False
            return next(self)

        if self.right_buckets:
            self.current_nodes = self.right_buckets.pop(0).get_nodes()
            self.left = True
            return next(self)

        raise StopIteration


class RoutingTable:
    def __init__(self, protocol, ksize, node):
        """
        @param node: The node that represents this server.  It won't
        be added to the routing table, but will be needed later to
        determine which buckets to split or not.
        """
        self.node = node
        self.protocol = protocol
        self.ksize = ksize
        self.flush()

    def flush(self):
        self.buckets = [KBucket(0, 2 ** 160, self.ksize, self.node.port)]

    def split_bucket(self, index):
        one, two = self.buckets[index].split()
        self.buckets[index] = one
        self.buckets.insert(index + 1, two)

    def lonely_buckets(self):
        """
        Get all of the buckets that haven't been updated in over
        an hour.
        """
        hrago = time.monotonic() - 3600
        return [b for b in self.buckets if b.last_updated < hrago]

    def remove_contact(self, node):
        index = self.get_bucket_for(node)
        self.buckets[index].remove_node(node)

    def is_new_node(self, node):
        index = self.get_bucket_for(node)
        return self.buckets[index].is_new_node(node)

    def add_contact(self, node):
        index = self.get_bucket_for(node)
        bucket = self.buckets[index]

        # this will succeed unless the bucket is full
        if bucket.add_node(node):
            return

        # Per section 4.2 of paper, split if the bucket has the node
        # in its range or if the depth is not congruent to 0 mod 5
        if bucket.has_in_range(self.node) or bucket.depth() % 5 != 0:
            self.split_bucket(index)
            self.add_contact(node)
        else:
            asyncio.ensure_future(self.protocol.call_ping(bucket.head()))

    def get_bucket_for(self, node):
        """
        Get the index of the bucket that the given node would fall into.
        """
        for index, bucket in enumerate(self.buckets):
            if node.long_id < bucket.range[1]:
                return index
        # we should never be here, but make linter happy
        return None

    def find_neighbors(self, node, k=None, exclude=None):
        k = k or self.ksize
        nodes = []
        for neighbor in TableTraverser(self, node):
            notexcluded = exclude is None or not neighbor.same_home_as(exclude)
            if neighbor.id != node.id and notexcluded:
                heapq.heappush(nodes, (node.distance_to(neighbor), neighbor))
            if len(nodes) == k:
                break

        return list(map(operator.itemgetter(1), heapq.nsmallest(k, nodes)))
