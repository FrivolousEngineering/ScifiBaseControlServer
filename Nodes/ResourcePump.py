from Nodes.Node import Node
from Nodes.Util import enforcePositive


class ResourcePump(Node):
    """
    A node that requires energy and produces a fluid as a result
    """
    def __init__(self, node_id: str, resource_type: str, amount: float = 10,  **kwargs) \
            -> None:
        """
        A node that creates a resource by consuming energy
        :param node_id: id of this node.
        :param resource_type: The resource that this node creates
        :param kwargs:
        """
        defaults = {"surface_area": 4.8,
                    "heat_convection_coefficient": 240,
                    "heat_emissivity": 0.73,
                    "min_performance": 0,
                    "usage_damage_factor": 0.21
                    }
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        self._resource_type = resource_type

        self._resources_required_per_tick["energy"] = 1
        self._resources_left_over[self._resource_type] = 0
        self._providable_resources.add(resource_type)
        self._amount = amount

    def _updateResourceRequiredPerTick(self) -> None:
        """
        If there were resources left over, we should request less resources next time round.
        """
        self._resources_required_per_tick["energy"] = self._performance * enforcePositive(self._original_resources_required_per_tick["energy"] * self.health_effectiveness_factor - (self._resources_left_over[self._resource_type] / self._amount))


    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        energy_gained = self.getResourceAvailableThisTick("energy")

        resource_produced = energy_gained * self._amount * self.effectiveness_factor
        self._markResourceAsCreated(self._resource_type, resource_produced)

        self._resources_produced_this_tick[self._resource_type] += resource_produced
        resource_available = resource_produced + self._resources_left_over[self._resource_type]

        # Attempt to "get rid" of the resource by offering it to connected sources.
        resource_left = self._provideResourceToOutgoingConnections(self._resource_type, resource_available)

        # It's entirely possible that no resource was generated this turn, but a bunch of resource was provided (since there
        # was some resource left over from the last tick!)
        self._resources_provided_this_tick[self._resource_type] += enforcePositive(resource_available - resource_left)

        self._resources_left_over[self._resource_type] = resource_left
