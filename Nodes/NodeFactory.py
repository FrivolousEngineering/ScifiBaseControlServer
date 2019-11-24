from Nodes.Node import Node
from typing import Dict

from Nodes import strToClass


class NodeFactory:
    @staticmethod
    def deserializeNode(key: str, data: Dict) -> Node:
        node_class = strToClass(data["type"])
        try:
            return node_class(key, **data)
        except TypeError as e:
            # Re-raise it, since the original is a bit unhelpful (since it doesn't say *what* class failed)
            raise TypeError("Unable to create %s" % node_class) from e



