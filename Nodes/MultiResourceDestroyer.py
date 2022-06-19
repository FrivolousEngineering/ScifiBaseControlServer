from Nodes.Constants import SPECIFIC_HEAT, WEIGHT_PER_UNIT
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
        defaults = {"has_settable_performance": False}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        for resource_type, amount in resources_required.items():
            self._resources_required_per_tick[resource_type.lower()] = amount

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        for resource_type, amount in self._resources_received_this_sub_tick.items():
            dumped_resources = amount * self.temperature * SPECIFIC_HEAT[resource_type] * WEIGHT_PER_UNIT[resource_type]

            # Since this destroys resources, we also need to remove the heat again. Note that this does mean that
            # if this node receives hot resources, it will increase in temperature. This is because it gets energy
            # based on the temperature of the node it received it from and destroys the resources based on its own
            # temperature (which hasn't updated yet)
            self.addHeat(-dumped_resources)
