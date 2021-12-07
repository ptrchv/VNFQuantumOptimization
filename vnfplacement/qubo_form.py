from os import link
import dimod
from vnfplacement.defines import TypeVNF, NodeProperty, LinkProperty, PropertyType
import math

class QuboFormulation:

    def __init__(self, discretization):
        self._qubo = None
        self._discretization = discretization

    @property
    def qubo(self):
        return self._qubo

    #extracts information from varialble name
    def _var_to_ids(self, var):
        var = var.replace("(","").replace(")","")
        ids = [id for id in var.split("_")[1:]]
        linkID = (int(ids[0].split("-")[0]), int(ids[0].split("-")[1]))
        sID = int(ids[1])
        fID = (int(ids[2].split("-")[0]), int(ids[2].split("-")[1]))     
        return linkID, sID, fID

    def _ids_to_var(self, startLinkID, endLinkID, sID, fID):
        return f"L_({startLinkID}-{endLinkID})_{sID}_({fID}-{fID+1})"
    
    # create variables for formulation
    def _create_variables(self, bqm, netw):
        for linkID in netw.links().keys():
            # check link edges are initialized nodes
            if not netw.is_used(linkID[0]) or not netw.is_used(linkID[1]):
                print(f"[WARNING]: Link {linkID} won't be considered")
                continue
            # iterate on every vnf of every chain
            for sID, sfc in netw.sfcs.items():
                for fID in sfc.vnfs.keys():
                    sfc_len = max(sfc.vnfs.keys())
                    if fID < sfc_len:
                        #consider link in both directions
                        bqm.add_variable(self._ids_to_var(linkID[0], linkID[1], sID, fID))
                        bqm.add_variable(self._ids_to_var(linkID[1], linkID[0], sID, fID))

            # # both links are servers
            # if netw.is_server(linkID[0]) and netw.is_server(linkID[1]):
            #     for sID, sfc in netw.sfcs().items():
            #         for fID in sfc.vnfs().keys():
            #             if fID != max(sfc.vnfs().keys()):
            #                 bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F({fID}-{fID+1})")

            # # one link is entry/exit
            # elif netw.is_server(linkID[0]) or netw.is_server(linkID[1]):
            #     for sID, sfc in netw.sfcs().items():
            #         bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F(START-0)")
            #         bqm.add_variable(f"y_L({linkID[0]}-{linkID[1]})_C{sID}_F({max(sfc.vnfs().keys())}-END)")
        return bqm

    def _add_node_cost(self, bqm, netw):
        for var in bqm.variables:
            # ids from varible 
            linkID, sID, fID = self._var_to_ids(var)

            # objects from id
            sfc = netw.sfcs[sID]         
            vnf1 = sfc.vnfs[fID[0]]
            node1 = netw.nodes[linkID[0]]   

            # add node cost for each vnf requirement
            for req, resQt in vnf1.requirements.items():
                resCost = node1[PropertyType.COST][req]
                bqm.add_linear(var, resCost * resQt) 

            # if last link add cost of second node
            vnf2 = sfc.vnfs[fID[1]]
            node2 = netw.nodes[linkID[1]]
            if fID[1] == len(sfc.vnfs) - 1:
                for req, resQt in vnf2.requirements.items():
                    resCost = node2[PropertyType.COST][req]
                    bqm.add_linear(var, resCost * resQt)

    def _add_link_cost(self, bqm, netw):
        for var in bqm.variables:
            # server is used if exit link is used
            linkID, sID, fID = self._var_to_ids(var)

            # get sfc resources and link costs
            sfc_res = netw.sfcs[sID].get_properties(PropertyType.RESOURCE)
            link_cost = netw.links[linkID][PropertyType.COST]

            # add link cost to bqm
            for res, resQt in sfc_res.items():
                resCost = link_cost[res] # exception if not present
                bqm.add_linear(var, resQt*resCost)
    
    def _node_res_constraint(self, bqm, netw):
        
        # for doing this you can use a constrained binary model
        # but how are the slack variables generated?       

        for nID, nodeP in netw.nodes.items():
            #variables containing nodeID
            varList = [v for v in list(bqm.variables) if self._var_to_ids(v)[0][0] == nID]
            print(varList)                   
            for res, resQt in nodeP[PropertyType.RESOURCE].items():
                bqmConstraint = dimod.BinaryQuadraticModel(dimod.BINARY)
                print(res, resQt)
                for v in varList:
                    linkID, sID, fID = self._var_to_ids(v)
                    resConsumed = netw.sfcs[sID].vnfs[fID[0]].requirements[res]
                    # bqmConstraint.add_linear_inequality_constraint --> this is not present in the documentation
                    #https://support.dwavesys.com/hc/en-us/community/posts/4413670491159-BQM-problem-adding-an-inequality-constraint
                break
            #     # for
            #     # print(math.ceil(resQt/self._discretization[res]))
            #     print(nID, res)

        
        
        
        # cqm = dimod.ConstrainedQuadraticModel()
        # cqm.set_objective(bqm)
        # bqm_constr = dimod.BinaryQuadraticModel(dimod.BINARY)
        # bqm_constr.add_linear("y_L(0-3)_C0_F(0-1)", 11)
        # bqm_constr.add_linear("y_L(0-3)_C0_F(1-2)", 12)
        # bqm_constr.add_linear("y_L(0-5)_C0_F(START-0)", 13)
        # bqm_constr.add_linear("y_L(0-5)_C0_F(2-END)", 14)
        # bqm_constr.add_linear("y_L(0-6)_C0_F(START-0)", 15)
        # bqm_constr.add_linear("y_L(0-6)_C0_F(2-END)", 16)
        # cqm.add_constraint(bqm_constr, sense="<=", rhs=5000, label='node_storage')
        # print(bqm_constr)
        # print(cqm)
        # print(cqm.variables)
        # print(cqm.constraints)
        
        
        
        # print(cqm)
        # print(cqm.variables)
        

    def generate_qubo(self, netw):
        # create bmq instance
        bqm = dimod.BinaryQuadraticModel(dimod.BINARY)

        # check if sfc are not empty
        for cid, sfc in netw.sfcs.items():
            if not sfc.vnfs:
                raise ValueError(f"{sfc} is an empty SFC")      

        # # check if sfc are not empty
        # for cid, sfc in netw.sfcs().items():
        #     print(cid)
        #     for fid, vnf in sfc.vnfs().items():
        #         print(f"f {fid}")      

        # build model
        self._create_variables(bqm, netw)
        self._add_node_cost(bqm, netw)
        self._add_link_cost(bqm, netw)
        self._node_res_constraint(bqm, netw)
        
        # # self._node_res_constraint(bqm, netw)           
        # print(bqm)
        # print("")
        # print(len(bqm.variables))
        # print(bqm.variables)

        # self._qubo = bqm
        


    
    
    


