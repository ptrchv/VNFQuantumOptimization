from enum import Enum

class TypeVNF(Enum):
    FIREWALL = 1
    NAT = 2
    IDS = 3
    PROXY = 4
    BUSINESS_LOGIC = 5

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