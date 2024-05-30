# models/node.py
from pydantic import BaseModel

from enum import Enum

class NodeType(Enum):
    wifi = "wifi"
    lora = "lora"

class Node(BaseModel):
    latitude: float
    longitude: float
    node_type: NodeType  # 'wifi' or 'lora'


