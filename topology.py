#!/usr/bin/python

class DRRouter(object):
    "Distributed routers"
    def __init__(self, name, topo=None):
        """Create router with:

        Attributes:
            @name: unique ID
            @topo: a dictionary of router name to its corresponding row and column
                in the network matrix. Row(a dictionary) stores outgoing link cost
                from this router; Column(a dictionary) stores incoming link cost
                to this router. A complete @topo represent the network's entire to
                pology.Router should use it to create graph weight matrix
                @self.network_matrix.
            @recv_from: list of routers can be reached from
            @recv_buffer: a dictionary storing the messages received from
                other routers
            @converged: indicate if @self.topo is complete
        """
        super(DRRouter, self).__init__()
        self.name = name
        self.topo = topo

        self.recv_from = [] # send @self.topo to them
        self.discover_neighbors()

        self.recv_buffer = {}
        self.network_matrix = []
        self.converged = False

    def discover_neighbors(self):
        """Discovery routers that can be reached from.
        """
        if self.name in self.topo.keys():
            col = self.topo[self.name][1] # get column/incoming link of that tuple
            for src in col.keys():
                if src not in self.recv_from:
                    self.recv_from.append(src)

    def recv_msg(self, msg):
        """Put @msg into @self.recv_buffer
        @msg is a tuple/entry to be added to buffer:
            msg[0] is the router name, msg[1] stores a tuple of (row, col)
        """
        if msg[0] not in self.recv_buffer.keys():
            self.recv_buffer[msg[0]] = msg[1]

    def update_topo(self):
        """Handle all the messages in the receive buffer
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
    """return DRRouter object with provided router name
    """
    for r in routers:
        if r.name == name:
            return r
    return None

def SimulateTopologyDiscovery():
    """Simulate the topology discovery process
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
                    topo_base_file1.write("%d  %s\n" % (iter_count, sorted(r.topo.items())))
                    r1_progress.append(saw / num_routers * 100)
                if r.name == 'r6':
                    topo_base_file6.write("%d  %s\n" % (iter_count, sorted(r.topo.items())))
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

if __name__ == '__main__':
    SimulateTopologyDiscovery()




