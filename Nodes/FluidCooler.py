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

        # Also try to pump up resources!
        self._resources_required_per_tick[resource_type] = fluid_per_tick

    def update(self) -> None:
        super().update()

        resource_available = self.getResourceAvailableThisTick(self._resource_type)
        resource_left = self._provideResourceToOutogingConnections(self._resource_type, resource_available)
        self._amount = resource_left
