#!/usr/bin/python

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
        converged: indicate if @self.topo is complete
        """
        super(DRRouter, self).__init__()
        self.name = name
        self.topo = topo

        self.recv_from = [] # send @self.topo to them

        self.discover_neighbors()

        self.recv_buffer = {}

        self.routing_table = {}

        self.converged = False

    def discover_neighbors(self):
        """Discovery routers that this router can be reached from"""
        if self.name in self.topo.keys():
            col = self.topo[self.name][1] # get column/incoming link of that tuple
            for src in col.keys():
                if src not in self.recv_from:
                    self.recv_from.append(src)

    def recv_msg(self, msg):
        """Put @msg into @self.recv_buffer

        msg -- a tuple/entry to be added to buffer
        msg[0] -- the router name
        msg[1] -- stores a tuple of (row, col)
        """
        if msg[0] not in self.recv_buffer.keys():
            self.recv_buffer[msg[0]] = msg[1]

    def update_topo(self):
        """Handle all the messages in the receive buffer

        Return updated -- a flag to tell if @self.topo is updated
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

        Return adjacents: a list of router names
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
        if not self.converged:
            return
        heap = []
        for router_name in self.topo.keys():
            adjacents = self.discover_adjacents(router_name)
            u = DRNode(router_name, adjacents)
            if u.name == self.name:
                u.dist = 0
            heap.append(u)

        while heap:
            heap.sort(key=lambda node: node.dist, reverse=False)
            u = heap.pop(0)
            self.routing_table[u.name] = {'dist': u.dist, 'pi': u.pi}
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
        print "Routing table for %s" % self.name
        print '-' * 38
        for dst in self.routing_table.keys():
            print "%s\tcost = %d\tnext hop = %s" % (dst, \
                self.routing_table[dst]['dist'], self.routing_table[dst]['next'])
        print '-' * 38
        print

class DRNode(object):
    def __init__(self, name, adjacents):
        super(DRNode, self).__init__()
        self.name = name
        # use an arbitrary large value as infinity
        self.dist = 999999999
        self.pi = None
        self.adjacents = adjacents

def get_node_by_name(name, nodes):
    for n in nodes:
        if n.name == name:
            return n
    return None

def get_router_by_name(name, routers):
    """Search DRRouter object with provided router name

    name -- the name of the router
    routers -- all routers in the network
    """
    for r in routers:
        if r.name == name:
            return r
    return None

def SimulateTopologyDiscovery():
    """Simulate the topology discovery process"""
    r1 = DRRouter('r1', {'r1' : ({'r2':3},
                                 {'r2':4})})
    r2 = DRRouter('r2', {'r2' : ({'r1':4, 'r3':6},
                                 {'r1':3, 'r6':8})})
    r3 = DRRouter('r3', {'r3' : ({'r4':7},
                                 {'r2':6, 'r6':5})})
    r4 = DRRouter('r4', {'r4' : ({'r5':11},
                                 {'r3':7})})
    r5 = DRRouter('r5', {'r5' : ({'r6':9},
                                 {'r4':11})})
    r6 = DRRouter('r6', {'r6' : ({'r2':8, 'r3':5},
                                 {'r5':9})})

    routers = [r1, r2, r3, r4, r5, r6]

    # for router in routers:
    #     print router.name, "will recv from", router.recv_from

    updated = True
    iter_count = 1

    num_routers = float(len(routers))

    saw = float(len(r1.topo.keys()))
    p0 = saw / num_routers * 100
    r1_progress = [p0]
    saw = float(len(r6.topo.keys()))
    p0 = saw / num_routers * 100
    r6_progress = [p0]

    topo_base_file1 = open('r1.topo', 'w+')
    topo_base_file6 = open('r6.topo', 'w+')
    while updated:
        for r in routers:
            for n in r.recv_from:
                router_n = get_router_by_name(n, routers)
                for n_name, n_row_col in router_n.topo.items():
                    n_msg = (n_name, n_row_col)
                    r.recv_msg(n_msg)

        updated = False
        for r in routers:
            if r.update_topo():
                updated = True
                saw = float(len(r.topo.keys()))
                if r.name == 'r1':
                    topo_base_file1.write("%d  %s\n" % \
                                    (iter_count, sorted(r.topo.items())))
                    r1_progress.append(saw / num_routers * 100)
                if r.name == 'r6':
                    topo_base_file6.write("%d  %s\n" % \
                                    (iter_count, sorted(r.topo.items())))
                    r6_progress.append(saw / num_routers * 100)

        iter_count += 1

    r1_progress.append(100)
    r6_progress.append(100)
    i = 0
    progress_file = open('progress.dat', 'w+')
    for p1, p6 in zip(r1_progress, r6_progress):
        progress_file.write("%d\t%3.3f\t%3.3f" % (i, p1, p6))
        i += 1
    progress_file.close()

    for r in routers:
        r.converged = True
        r.create_routing_table()
        r.print_routing_table()

if __name__ == '__main__':
    SimulateTopologyDiscovery()


