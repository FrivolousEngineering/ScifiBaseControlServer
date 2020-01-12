from Nodes.ResourceStorage import ResourceStorage


class FluidCooler(ResourceStorage):
    """
    A fairly simple node that has a high surface area and heat emissivity.
    It can accept a certain resource, which it cools down (because of it's large surface and heat emissivity)
    """
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float, **kwargs) -> None:
        super().__init__(node_id, resource_type, 0, fluid_per_tick, **kwargs)
        self._fluid_per_tick = fluid_per_tick
        self._surface_area = 8
        self._heat_emissivity = 0.9

        # Also try to pump up resources!
        self._resources_required_per_tick[resource_type] = fluid_per_tick

    def _updateResourceRequiredPerTick(self) -> None:
        self._resources_required_per_tick[self._resource_type] = max(0., self._fluid_per_tick - self._amount)

    def update(self) -> None:
        # First, we store the resources other nodes *gave* us (these are already added!)
        resource_already_added = self._resources_received_this_tick.get(self._resource_type, 0)

        # Then we check how much resources in total we got this turn (aka; how much after we also requested resources)
        super().update()
        resource_available = self.getResourceAvailableThisTick(self._resource_type)

        # Now we can figure out how much we really have right now.
        self._amount = self._amount + resource_available - resource_already_added

        # Then we try to give as much away as possible.
        resource_left = self._provideResourceToOutogingConnections(self._resource_type, self._amount)
        self._amount = resource_left

        # Finally, update how much the cooler should try to pull in.
        self._updateResourceRequiredPerTick()
