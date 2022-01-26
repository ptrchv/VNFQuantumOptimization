from enum import Enum

# PROBLEM FORMULATION
class NodeProperty(Enum):
    CPU = 'cpu'             #num_cpu
    MEMORY = 'memory'       #GB
    STORAGE = 'storage'     #GB

class LinkProperty(Enum):
    BANDWIDTH = 'bandwidth' #GBps
    DELAY = 'delay'         #ms

class PropertyType(Enum):
    RESOURCE = 'resource'
    COST = 'cost'
    DRAWBACK = 'drawback'


class QuboExpression(Enum):
    NODE_COST = "node_cost"
    LINK_COST = 'link_cost'
    NODE_RES = 'node_res'
    LINK_RES = 'link_res'
    LINK_DRAW = 'link_draw'
    ALLOCATION = 'allocation'
    CONTINUITY = 'continuity'