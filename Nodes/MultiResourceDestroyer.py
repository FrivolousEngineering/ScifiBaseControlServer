from Nodes.Node import Node

from typing import Dict


class MultiResourceDestroyer(Node):
    """
    A  Multi Resource destroyer is, as the name implies, a node that accepts (and destroys) a given set of resources
    every tick.
    """
    def __init__(self, node_id: str, resources_required: Dict[str, float], **kwargs) -> None:
        """
        Create a Resource destroyer that accepts (and destroys) a given resource every tick.
        :param node_id: Unique identifier of the node
        :param resources_required: What resources should it destroy (key / value pairs!)
        :param kwargs:
        """
        super().__init__(node_id, **kwargs)

        for resource_type, amount in resources_required.items():
            self._resources_required_per_tick[resource_type.lower()] = amount
