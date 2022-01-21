from Nodes.Node import Node
from Nodes.Util import enforcePositive


class ResourceGenerator(Node):
    """
    A Resource generator is, as the name implies, a node that generates a given resource every tick.
    """
    def __init__(self, node_id: str, resource_type: str, amount: float, **kwargs) -> None:
        """
        Create a Resource generator that generates a given resource every tick.
        :param node_id: Unique identifier of the node
        :param resource_type: What type of resource should it produce?
        :param amount: How much of the resource should it produce every tick?
        :param kwargs:
        """
        super().__init__(node_id, **kwargs)
        self._resource_type = resource_type.lower()
        self._amount = amount
        self._providable_resources.add(resource_type)

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        # Bit of a hack, but since we're creating resources out of thin air here (without creating more energy)
        # It goes a bit wonky otherwise. So we just reset the heat to back to what it was.
        stored_heat = self._stored_heat
        resources_left = self._provideResourceToOutgoingConnections(self._resource_type, self._amount)
        self._stored_heat = stored_heat
        self._resources_produced_this_tick[self._resource_type] += enforcePositive(self._amount - resources_left)
