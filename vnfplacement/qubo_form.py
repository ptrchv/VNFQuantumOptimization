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

    # creates variable name
    def _ids_to_var(self, startLinkID, endLinkID, sID, fID):
        return f"L_({startLinkID}-{endLinkID})_{sID}_({fID}-{fID+1})"

    # extract variable with given nodes, chaing, etc...
    def _vars_containing(self, var_list, **kwargs):
        settings = {
            "start_node" : None,
            "end_node" : None,
            "cID" : None,
            "fID_start" : None,
            "fID_end" : None
        }
        # check if wrong parameter name was passed
        wrong_pars = [p for p in kwargs.keys() if p not in settings.keys()]
        if wrong_pars != []:
            raise TypeError(f'\'{wrong_pars}\' are not valid parameters')

        #update parameters
        settings.update(kwargs)
        
        # variables selection
        if settings["start_node"] is not None:
            var_list = [v for v in var_list if self._var_to_ids(v)[0][0] == settings["start_node"]]
        if settings["end_node"] is not None:
            var_list = [v for v in var_list if self._var_to_ids(v)[0][1] == settings["end_node"]]
        if settings["cID"] is not None:
            var_list = [v for v in var_list if self._var_to_ids(v)[1] == settings["cID"]]
        if settings["fID_start"] is not None:
            var_list = [v for v in var_list if self._var_to_ids(v)[2][0] == settings["fID_start"]]
        if settings["fID_end"] is not None:
            var_list = [v for v in var_list if self._var_to_ids(v)[2][1] == settings["fID_end"]]
        return var_list
    
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
                    max_cID = max(sfc.vnfs.keys())
                    if fID < max_cID:
                        #consider link in both directions
                        bqm.add_variable(self._ids_to_var(linkID[0], linkID[1], sID, fID))
                        bqm.add_variable(self._ids_to_var(linkID[1], linkID[0], sID, fID))
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
    
    # every fuction implemented by exactly one node
    def _vnf_allocation_constraint(self, bqm, netw, lagrange_multiplier):
        for cID, sfc in netw.sfcs.items():
            for fID in sfc.vnfs.keys():
                max_cID = max(sfc.vnfs.keys())
                if fID < max_cID:
                    #list of all variables with specified fID and cID
                    var_list = [v for v in list(bqm.variables) if self._var_to_ids(v)[1] == cID and self._var_to_ids(v)[2][0] == fID]
                    #create list of tuples (variable, bias)
                    terms = [(v, 1) for v in var_list]
                    bqm.add_linear_equality_constraint(
                        terms = terms,
                        lagrange_multiplier = lagrange_multiplier,
                        constant = -1
                    )
    
    # physical links of consecutive sfc segments must be adjacent
    def _sfc_continuity_constraint(self, bqm, netw, lagrange_multiplier):
        for nID in netw.nodes.keys():
            for cID, sfc in netw.sfcs.items():
                for fID in sfc.vnfs.keys():
                    #first sfc segment on first link can't be last segment
                    if fID < max(sfc.vnfs.keys()) - 1:
                        var_list_1 = self._vars_containing(bqm.variables, end_node = nID, cID = cID, fID_start = fID)
                        var_list_2 = self._vars_containing(bqm.variables, start_node = nID, cID = cID, fID_start = fID + 1)
                        terms = [(v, 1) for v in var_list_1] + [(v, -1) for v in var_list_2]
                        bqm.add_linear_equality_constraint(
                            terms = terms,
                            lagrange_multiplier = lagrange_multiplier,
                            constant = 0
                        )

    # do not exceed node resources
    #https://support.dwavesys.com/hc/en-us/community/posts/4413670491159-BQM-problem-adding-an-inequality-constraint
    def _node_res_constraint(self, bqm, netw, discretization):
        # for all nodes
        for nID, nodeP in netw.nodes.items():
            var_list = self._vars_containing(bqm.variables, start_node = nID)
            # for all resource types
            for res, resQt in nodeP[PropertyType.RESOURCE].items():
                terms = []
                for v in var_list:
                    linkID, sID, fID = self._var_to_ids(v)
                    res_consumed = netw.sfcs[sID].vnfs[fID[0]].requirements[res]
                    terms.append((v,res_consumed))
                    #print(res, resQt, res_consumed)
                max_slack =math.ceil(resQt/discretization[res])
                print(max_slack)
                num_slack = math.ceil(math.log(max_slack, 2)) + 1
                print(num_slack)

                
                #print(discretization[res])
            break
                
                    # bqmConstraint.add_linear_inequality_constraint --> this is not present in the documentation
                    
            
            #     # for
            #     # print(math.ceil(resQt/self._discretization[res]))
            #     print(nID, res)
    
    def generate_qubo(self, netw):
        # create bmq instance
        bqm = dimod.BinaryQuadraticModel(dimod.BINARY)

        # check that there are no empty sfcs
        for cid, sfc in netw.sfcs.items():
            if not sfc.vnfs:
                raise ValueError(f"{sfc} is an empty SFC")

        # model variables
        self._create_variables(bqm, netw)

        # cost function
        self._add_node_cost(bqm, netw)
        self._add_link_cost(bqm, netw)

        # cost constraints
        self._node_res_constraint(bqm, netw, self._discretization)

        # structure constraints
        #self._vnf_allocation_constraint(bqm, netw, lagrange_multiplier = 10) #to tweak
        #self._sfc_continuity_constraint(bqm, netw, lagrange_multiplier = 10)       

        self._qubo = bqm
        


    
    
    


