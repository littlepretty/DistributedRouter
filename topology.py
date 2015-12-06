#!/usr/bin/python

from drrouter import DRRouter

def simulate_topology_discovery():
    """Simulate the topology discovery process"""
    def get_router_by_name(name, routers):
        """Search DRRouter object with provided router name

        name -- the name of the router
        routers -- all routers in the network
        """
        for r in routers:
            if r.name == name:
                return r
        return None

    # initialize router's topology database
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
        print router.name, "will recv from", router.recv_from

    iter_count = 1
    num_routers = float(len(routers))

    # initialize progress array at iteration 0
    saw = float(len(r1.topo.keys()))
    p0 = saw / num_routers
    r1_progress = [p0]
    saw = float(len(r6.topo.keys()))
    p0 = saw / num_routers
    r6_progress = [p0]

    topo_base_file1 = open('r1.topo', 'w+')
    topo_base_file6 = open('r6.topo', 'w+')

    # termination flag: if all routers converged?
    updated = True
    while updated:
        # scatter phase: receive from its neighbors
        for r in routers:
            for n in r.recv_from:
                router_n = get_router_by_name(n, routers)
                for n_name, n_row_col in router_n.topo.items():
                    n_msg = (n_name, n_row_col)
                    r.recv_msg(n_msg)

        # gather phase: update topology database
        updated = False
        for r in routers:
            if r.update_topo():
                updated = True
                saw = float(len(r.topo.keys()))
                if r.name == 'r1':
                    topo_base_file1.write("%d  %s\n" % \
                        (iter_count, sorted(r.topo.items())))
                    r1_progress.append(saw / num_routers)
                if r.name == 'r6':
                    topo_base_file6.write("%d  %s\n" % \
                        (iter_count, sorted(r.topo.items())))
                    r6_progress.append(saw / num_routers)

        iter_count += 1
    # extra progress after stable
    r1_progress.append(1)
    r6_progress.append(1)

    # write progress results to file
    i = 0
    progress_file = open('progress.dat', 'w+')
    for p1, p6 in zip(r1_progress, r6_progress):
        progress_file.write("%d\t%3.3f\t%3.3f" % (i, p1, p6))
        i += 1
    progress_file.close()

    # run Dijkstra's shortest path on every router
    for r in routers:
        r.converged = True
        r.create_routing_table()
        r.print_routing_table()

if __name__ == '__main__':
    simulate_topology_discovery()

