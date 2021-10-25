import dimod
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType

class QuboFormulation:

    def __init__(self):
        self.qubo = None

    def get_qubo(self):
        return self.qubo

    def var_to_ids(self, var):
        var = var.replace("(","").replace(")","")
        ids = [id[1:] for id in var.split("_")[1:]]
        linkID = (int(ids[0].split("-")[0]), int(ids[0].split("-")[1]))
        sID = int(ids[1])
        fID = ids[2].split("-")
        fID[0] = int(fID[0]) if fID[0] != "START" else fID[0]
        fID[1] = int(fID[1]) if fID[1] != "END" else fID[1]
        fID = (fID[0], fID[1])
        return linkID, sID, fID

    def generate_qubo(self, netw):
        # create bmq instance
        bqm = dimod.BinaryQuadraticModel(dimod.BINARY)

        # check if sfc are not empty
        for s in netw.sfcs:
            if not s[0].vnfs:
                raise ValueError(f"{s} is an empty SFC")

        # create variables
        self.create_variables(bqm, netw)
        print(bqm.variables)

        for var in bqm.variables:
            print(self.var_to_ids(var))

        # node cost


    def create_variables(self, bqm, netw):
        # create all variables
        for linkID in netw.links().keys():
            # check link edges are valid
            if not netw.is_used(linkID[0]) or not netw.is_used(linkID[1]):
                print(f"[WARNING]: Link {linkID} won't be considered")
                continue
            # check if both are servers
            if netw.is_server(linkID[0]) and netw.is_server(linkID[1]):
                sID = 0
                for s in netw.sfcs:
                    for fID in range(len(s[0].vnfs)-1):
                        bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F({fID}-{fID+1})")
                    sID+=1
            #check if first is server
            elif netw.is_server(linkID[0]) or netw.is_server(linkID[1]):
                sID = 0
                for s in netw.sfcs:
                    bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F(START-0)")
                    bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F({len(s[0].vnfs)}-END)")
                sID += 1
        return bqm

        # # node cost
        # for var in bqm.variables:
        #     ids = self.var_to_ids(var)
        #     node, sfc, vnf = netw.ids_to_objs(ids)

        #     # skip in node is entry/exit point
        #     if netw.is_entry(ids[0]) or not netw.is_used(ids[0]):
        #         continue

        #     # add terms
        #     for k, resQt in vnf.requirements.items():
        #         resCost = node[PropertyType.COST][k]
        #         bqm.add_linear(var, resCost * resQt)

        # # link cost
        # for var1 in bqm.variables:
        #     for var2 in bqm.variables:
        #         ids1 = self.var_to_ids(var1)
        #         ids2 = self.var_to_ids(var2)

        #         # different nodes, same chain, consecutive vnfs
        #         if ids1[0] == ids2[0]:
        #             continue
        #         if ids1[1] != ids2[1]:
        #             continue
        #         if ids1[2] != ids2[2] + 1:
        #             continue

        #         # get sfc properties
        #         node, sfc, vnf = netw.ids_to_objs(ids)
        #         sfc_res = sfc.get_properties(PropertyType.RESOURCE)

        #         # get edge properties           
        #         edge_cost = None
        #         if netw.are_linked(ids1[0], ids2[0]):
        #             edge_cost = netw.get_link(ids1[0], ids2[0])[PropertyType.COST]
        #         else:
        #             edge_cost = netw.detatched[PropertyType.COST]

        #         # add quadratic terms
        #         for res, resQt in sfc_res.items():
        #             resCost = edge_cost[res] # exception if not present
        #             bqm.add_quadratic(var1, var2, resQt*resCost)

        # print(bqm)
            # print(node, sfc, vnf)

        #     # skip in node is entry/exit point
        #     if node["server"] == False or node["server"] is None:
        #         continue
        #     for k, resQt in vnf.requirements.items():
        #         resCost = node[PropertyType.COST][k]
        #         bqm.add_linear(var, resCost * resQt)
        # print(bqm)
                

    
    
    


