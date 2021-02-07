from Nodes.Node import Node


class ResourceDestroyer(Node):
    """
    A Resource Destroyer is, as the name implies, a node that accepts (and destroys) a given resource every tick.
    """
    def __init__(self, node_id: str, resource_type: str, amount: float, **kwargs) -> None:
        """
        Create a Resource destroyer that accepts (and destroys) a given resource every tick.
        :param node_id: Unique identifier of the node
        :param resource_type: What type of resource should it accept & destroy?
        :param amount: How much of the resource should it accept & destroy every tick?
        :param kwargs:
        """
        super().__init__(node_id, **kwargs)
        self._resources_required_per_tick[resource_type.lower()] = amount
