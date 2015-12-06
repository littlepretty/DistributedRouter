#!/usr/bin/python

class DRNode(object):
    "Extra info used by a router to compute shortest path"
    def __init__(self, name, adjacents):
        """Create DRNode object

        name(str) -- unique name of the router
        adjacents(list) -- all the names of its adjacents
        dist -- distance to this node from the running router
        pi -- previous hop to this node from running router
        """
        super(DRNode, self).__init__()
        self.name = name
        self.adjacents = adjacents
        # use an arbitrary large value as infinity
        self.dist = 999999999
        self.pi = None

class DRRouter(object):
    "Distributed routers"
    def __init__(self, name, topo=None):
        """Create router obect.

        name: unique string ID
        topo: Topology database: map router name to its corresponding
            row and column in the network matrix. Row(a dictionary) stores
            outgoing link cost from this router; column(a dictionary) stores
            incoming link cost to this router.
        recv_from: list of routers can be reached from
        recv_buffer: a dictionary storing the messages received from other routers
        converged: indicate if topology database is complete
        routing_table: next hop to certain destination based on Dijkstra's SP
        """
        super(DRRouter, self).__init__()
        self.name = name
        self.topo = topo
        self.recv_from = [] # send @self.topo to them
        self.discover_neighbors()
        self.recv_buffer = {}
        self.converged = False
        self.routing_table = {}

    def discover_neighbors(self):
        """Discovery routers that this router can be reached from"""
        if self.name in self.topo.keys():
            col = self.topo[self.name][1] # get column/incoming link of that tuple
            for src in col.keys():
                if src not in self.recv_from:
                    self.recv_from.append(src)

    def recv_msg(self, msg):
        """Put messages into receiver's buffer

        msg -- a tuple/entry to be added to buffer
        msg[0] -- the router name
        msg[1] -- stores a tuple of (row, col)
        """
        if msg[0] not in self.recv_buffer.keys():
            self.recv_buffer[msg[0]] = msg[1]

    def update_topo(self):
        """Handle all the messages in the receive buffer

        updated -- return a flag to tell if @self.topo is updated
        """
        updated = False
        for router in self.recv_buffer.keys():
            if router not in self.topo.keys():
                self.topo[router] = self.recv_buffer[router]
                updated = True
        self.recv_buffer = {} # clear receive buffer
        return updated

    def discover_adjacents(self, router_name):
        """Discovery routers that a particular router can reach

        adjacents: return a list of router names
        """
        adjacents = []
        if self.converged:
            if router_name in self.topo.keys():
                row = self.topo[router_name][0]
                for dst in row.keys():
                    adjacents.append(dst)
        return adjacents

    def create_routing_table(self):
        """Dijkstra's shortest path algorithm"""
        def get_node_by_name(name, nodes):
            """Search DRNode in a list

            name -- provided search ID
            """
            for n in nodes:
                if n.name == name:
                    return n
            return None

        if not self.converged:
            return
        heap = []
        # create a node to each router in the network
        for router_name in self.topo.keys():
            adjacents = self.discover_adjacents(router_name)
            u = DRNode(router_name, adjacents)
            if u.name == self.name:
                u.dist = 0
            heap.append(u)

        while heap:
            heap.sort(key=lambda node: node.dist, reverse=False)
            # equivalent to heap.extract-min()
            u = heap.pop(0)
            self.routing_table[u.name] = {'dist': u.dist, 'pi': u.pi}
            # do relaxation for all u's neighbors
            for v_name in u.adjacents:
                v = get_node_by_name(v_name, heap)
                # v may be None if we have a loop in the topology
                if v and v.dist > u.dist + self.topo[u.name][0][v.name]:
                    v.dist = u.dist + self.topo[u.name][0][v.name]
                    v.pi = u
        # backtrack along the pi to get the next hop for this router
        for u_name in self.topo.keys():
            if u_name != self.name:
                next_name = u_name
                prev = self.routing_table[u_name]['pi']
                while prev.name != self.name:
                    next_name = prev.name
                    prev = prev.pi
                self.routing_table[u_name]['next'] = next_name
            else: # next hop to itself is itself
                self.routing_table[u_name]['next'] = u_name

    def print_routing_table(self):
        """Pretty print of router's routing table"""
        print "Routing table for %s" % self.name
        print '-' * 38
        for dst in self.routing_table.keys():
            print "%s\tcost = %d\tnext hop = %s" % (dst, \
                self.routing_table[dst]['dist'], self.routing_table[dst]['next'])
        print '-' * 38
        print

