from os import link
import dimod
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType

class QuboFormulation:

    def __init__(self):
        self.qubo = None

    def __var_to_ids(self, var):
        var = var.replace("(","").replace(")","")
        ids = [id[1:] for id in var.split("_")[1:]]
        linkID = (int(ids[0].split("-")[0]), int(ids[0].split("-")[1]))
        sID = int(ids[1])
        fID = ids[2].split("-")
        fID[0] = int(fID[0]) if fID[0] != "START" else fID[0]
        fID[1] = int(fID[1]) if fID[1] != "END" else fID[1]
        fID = (fID[0], fID[1])
        return linkID, sID, fID
    
    # create variables for formulation
    def __create_variables(self, bqm, netw):
        for linkID in netw.links().keys():
            # check link edges are valid
            if not netw.is_used(linkID[0]) or not netw.is_used(linkID[1]):
                print(f"[WARNING]: Link {linkID} won't be considered")
                continue

            # both links are servers
            if netw.is_server(linkID[0]) and netw.is_server(linkID[1]):
                for sID, sfc in netw.sfcs().items():
                    for fID in sfc.vnfs().keys():
                        if fID != max(sfc.vnfs().keys()):
                            bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F({fID}-{fID+1})")

            # one link is entry/exit
            elif netw.is_server(linkID[0]) or netw.is_server(linkID[1]):
                for sID, sfc in netw.sfcs().items():
                    bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F(START-0)")
                    bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F({max(sfc.vnfs().keys())}-END)")
        return bqm

    def __add_node_cost(self, bqm, netw):
        for var in bqm.variables:
            #server is used if exit link is used
            linkID, sID, fID = self.__var_to_ids(var)
            nodeID = linkID[0]

            # skip enty/exit points
            if fID[0] == "START":
                continue
            
            # add node cost to bqm
            vnf = netw.sfcs()[sID].vnfs()[fID[0]]
            node = netw.nodes()[nodeID]
            for req, resQt in vnf.requirements.items():
                resCost = node[PropertyType.COST][req]
                bqm.add_linear(var, resCost * resQt)

    def __add_link_cost(self, bqm, netw):
        for var in bqm.variables:
            # server is used if exit link is used
            linkID, sID, fID = self.__var_to_ids(var)

            # get sfc resources and link costs
            sfc_res = netw.sfcs()[sID].get_properties(PropertyType.RESOURCE)
            link_cost = netw.links()[linkID][PropertyType.COST]

            # add link cost to bqm
            for res, resQt in sfc_res.items():
                resCost = link_cost[res] # exception if not present
                bqm.add_linear(var, resQt*resCost)

    def generate_qubo(self, netw):
        # create bmq instance
        bqm = dimod.BinaryQuadraticModel(dimod.BINARY)

        # check if sfc are not empty
        for s in netw.sfcs().values():
            if not s.vnfs:
                raise ValueError(f"{s} is an empty SFC")

        # build model
        self.__create_variables(bqm, netw)
        self.__add_node_cost(bqm, netw)
        self.__add_link_cost(bqm, netw)           
        print(bqm)
                

    
    
    


