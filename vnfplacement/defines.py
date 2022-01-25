from enum import Enum

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