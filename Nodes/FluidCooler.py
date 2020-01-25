from typing import cast

from Nodes.ResourceStorage import ResourceStorage


class FluidCooler(ResourceStorage):
    """
    A fairly simple node that has a high surface area and heat emissivity.
    It can accept a certain resource, which it cools down (because of it's large surface and heat emissivity)
    """
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float, **kwargs) -> None:
        super().__init__(node_id, resource_type, 0, 2 * fluid_per_tick, **kwargs)
        self._fluid_per_tick = fluid_per_tick
        self._surface_area = 250
        self._heat_emissivity = 1

        # Also try to pump up resources!
        self._resources_required_per_tick[self._resource_type] = fluid_per_tick

    def _updateResourceRequiredPerTick(self) -> None:
        new_amount_required = self._fluid_per_tick
        storage_room_left = cast(float, self._max_storage) - self._amount
        if storage_room_left < self._fluid_per_tick:
            new_amount_required = storage_room_left

        self._resources_required_per_tick[self._resource_type] = max(0., new_amount_required)

    def update(self) -> None:
        # First, we store the resources other nodes *gave* us (these are already added!)
        resource_already_added = self._resources_received_this_tick.get(self._resource_type, 0)
        # Then we check how much resources in total we got this turn (aka; how much after we also requested resources)
        super().update()
        resource_available = self.getResourceAvailableThisTick(self._resource_type)
        # Now we can figure out how much we really have right now.
        self._amount = self._amount - resource_already_added

        # Then we try to give as much away as possible.
        resource_left = self._provideResourceToOutogingConnections(self._resource_type, self._amount)

        # Only at this point add the resources (so that they are cooled for at least one tick!)
        self._amount = resource_left + resource_available

        # Finally, update how much the cooler should try to pull in.
        self._updateResourceRequiredPerTick()
