import sys
from Nodes.Node import Node
from typing import Dict

from Nodes import strToClass


class NodeFactory:
    @staticmethod
    def deserializeNode(key: str, data: Dict) -> Node:
        node_class = strToClass(data["type"])
        return node_class(key, **data)



