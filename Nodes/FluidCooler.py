from Nodes.ResourceStorage import ResourceStorage


class FluidCooler(ResourceStorage):
    """
    A fairly simple node that has a high surface area and heat emissivity.
    It can accept a certain resource, which it cools down (because of it's large surface and heat emissivity)
    """
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float, **kwargs) -> None:
        super().__init__(node_id, resource_type, 0, fluid_per_tick, **kwargs)
        self._surface_area = 8
        self._heat_emissivity = 0.9

    def update(self) -> None:
        super().update()

        resource_available = self.getResourceAvailableThisTick(self._resource_type)
        resource_left = self._provideResourceToOutogingConnections(self._resource_type, resource_available)

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over[self._resource_type] = resource_left

        self._amount = resource_left
