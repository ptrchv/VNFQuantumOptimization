import random
import networkx as nx
import dimod
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType

color_switch = "yellow"
color_server = "orange"

#make node swith or server with probability prob
def node_class_rand(net, prob):
    for n in net.nodes:
        if (random.random() < prob):
            nx.set_node_attributes(net, {n:{"type":"switch", "color":"yellow"}})
        else:
            nx.set_node_attributes(net, {n:{"type":"server", "color":"orange"}})
    return net

#draw graph using color property of nodes
def draw_with_colors(net):
    cmap = list(nx.get_node_attributes(net, "color").values())
    nx.draw(net, node_color = cmap, with_labels = True)


def generate_qubo(self, netw):
    # create bmq instance
    bqm = dimod.BinaryQuadraticModel(dimod.BINARY)

    # create all variables
    for nodeID, node in netw.nodes().items():
        if not netw.is_used(nodeID):
            print(f"[WARNING]: Node {nodeID} won't be considered")
            continue
        sID = 0
        for s in netw.sfcs:
            fID = 0
            for f in s[0].vnfs:
                bqm.add_variable(f"x_N{nodeID}_C{sID}_F{fID}")
                fID+=1
            sID+=1
    print(bqm.variables)
    
    # node cost
    for var in bqm.variables:
        ids = self.var_to_ids(var)
        node, sfc, vnf = netw.ids_to_objs(ids)

        # skip in node is entry/exit point
        if netw.is_entry(ids[0]) or not netw.is_used(ids[0]):
            continue

        # add terms
        for k, resQt in vnf.requirements.items():
            resCost = node[PropertyType.COST][k]
            bqm.add_linear(var, resCost * resQt)

    # link cost
    for var1 in bqm.variables:
        for var2 in bqm.variables:
            ids1 = self.var_to_ids(var1)
            ids2 = self.var_to_ids(var2)

            # different nodes, same chain, consecutive vnfs
            if ids1[0] == ids2[0]:
                continue
            if ids1[1] != ids2[1]:
                continue
            if ids1[2] != ids2[2] + 1:
                continue

            # get sfc properties
            node, sfc, vnf = netw.ids_to_objs(ids)
            sfc_res = sfc.get_properties(PropertyType.RESOURCE)

            # get edge properties           
            edge_cost = None
            if netw.are_linked(ids1[0], ids2[0]):
                edge_cost = netw.get_link(ids1[0], ids2[0])[PropertyType.COST]
            else:
                edge_cost = netw.detatched[PropertyType.COST]

            # add quadratic terms
            for res, resQt in sfc_res.items():
                resCost = edge_cost[res] # exception if not present
                bqm.add_quadratic(var1, var2, resQt*resCost)

    print(bqm)