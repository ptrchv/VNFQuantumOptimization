from enum import Enum

class NodeProperty(Enum):
    CPU = 1         #num_cpu
    MEMORY = 2      #GB
    STORAGE = 3     #GB

class LinkProperty(Enum):
    BANDWIDTH = 1   #GBps
    DELAY = 2       #ms

class PropertyType(Enum):
    RESOURCE = 1
    COST = 2
    DRAWBACK = 3