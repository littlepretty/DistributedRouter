#!/usr/bin/python

class DRRouter(object):
    "Distributed routers"

    def __init__(self, name, topo=None):
        """Create router with:
        @name: unique ID
        @topo: a dictionary of router name to its corresponding row and column
        in the network matrix. Row(a dictionary) stores outgoing link cost
        from this router; Column(a dictionary) stores incoming link cost
        to this router. A complete @topo represent the network's entire topology.
        Router should use it to create graph weight matrix @self.network_matrix.
        @neighbors: list of routers can be reached from
        @recv_buffer: a dictionary storing the messages received from
        other routers
        @converged: indicate if @self.topo is complete
        """
        super(DRRouter, self).__init__()
        self.name = name
        self.topo = topo

        self.neighbors = [] # send @self.topo to them
        self.discover_neighbors()

        self.recv_buffer = {}
        self.network_matrix = []
        self.converged = False

    def discover_neighbors(self):
        """
        Discovery routers that can be reached from.
        """
        if self.name in self.topo.keys():
            row = self.topo[self.name][0] # get row of that tuple
            for dst in row.keys():
                if dst not in self.neighbors:
                    self.neighbors.append(dst)

    def recv_msg(self, msg):
        """
        Put @msg into @self.recv_buffer
        @msg is a tuple/entry to be added to buffer:
            msg[0] is the router name, msg[1] stores a tuple of (row, col)
        """
        if msg[0] not in self.recv_buffer.keys():
            self.recv_buffer[msg[0]] = msg[1]

    def update_topo(self):
        """
        Handle all the messages in the receive buffer
        @updated: return this flag to tell if @self.topo is updated
        """
        updated = False
        for router in self.recv_buffer.keys():
            if router not in self.topo.keys():
                self.topo[router] = self.recv_buffer[router]
                updated = True
        self.recv_buffer = {} # clear receive buffer
        return updated

    def create_graph_matrix(self):
        if self.converged:
            pass
    def create_routing_table(self):
        pass

def get_router_by_name(name, routers):
    """
    return DRRouter object providing a router name
    """
    for r in routers:
        if r.name == name:
            return r
    return None

def SimulateTopologyDiscovery():
    """
    Simulate the topology discovery process
    """
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
    for router in routers:
        print router.name, "will recv from", router.neighbors

    updated = True
    iter_count = 1
    num_routers = float(len(routers))
    while updated:
        for r in routers:
            for n in r.neighbors:
                router_n = get_router_by_name(n, routers)
                for n_name, n_row_col in router_n.topo.items():
                    n_msg = (n_name, n_row_col)
                    r.recv_msg(n_msg)

        updated = False
        for r in routers:
            if r.update_topo():
                updated = True
                saw = float(len(r.topo.keys()))
                print "%s saw %f%% of the network at %d iteration" % (r.name, saw / num_routers * 100, iter_count)

        iter_count += 1

    for r in routers:
        r.converged = True
        print r.topo

if __name__ == '__main__':
    SimulateTopologyDiscovery()




