from typing import cast

from Nodes.ResourceStorage import ResourceStorage
from Nodes.Util import enforcePositive


class Valve(ResourceStorage):
    """
    A valve is a special kind of resource storage; it does have a performance and it can also request resources from
    other resource providers that it's connected to.
    """
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float, **kwargs) -> None:
        """

        :param node_id: unique id of the node
        :param resource_type: The resource type that this valve accepts
        :param fluid_per_tick: units of resource that this valve can handle per tick. It will request this amount from
        connected nodes.
        :param kwargs:
        """
        # Update the defaults like this so that the actual property can be set by base class
        defaults = {"heat_convection_coefficient": 0.2}
        defaults.update(kwargs)

        super().__init__(node_id, resource_type, 0, 2.5 * fluid_per_tick, **kwargs)
        self._fluid_per_tick = fluid_per_tick
        self._max_resources_requestables_per_tick = fluid_per_tick

        # A valve cooler pretends to be a resource storage, but it shouldn't display this.
        #self.additional_properties.remove("amount_stored")

        # Also try to pump up resources!
        self._optional_resources_required_per_tick[self._resource_type] = fluid_per_tick
        self._min_performance = 0
        self._description = "This device pumps {resource_type} from all incomming connections and provides them to" \
                            " all of it's outgoing connections."
        self._description = self._description.format(resource_type = resource_type)
        self._performance_change_factor = 1

        self._has_settable_performance = True

    def _updateResourceRequiredPerTick(self) -> None:
        """
        If there were resources left over, we should request less resources next time round.
        """
        new_amount_required = self._fluid_per_tick * self._performance
        storage_room_left = cast(float, self._max_storage) - self._amount
        if storage_room_left < new_amount_required:
            new_amount_required = storage_room_left
        self._optional_resources_required_per_tick[self._resource_type] = max(0., new_amount_required)

    def _setPerformance(self, new_performance) -> None:
        self._updateResourceRequiredPerTick()
        super()._setPerformance(new_performance)

        # HACK: Make it a bit bigger than it should be. This prevents weird fluctuations if you put two valves in a row.
        self._max_storage = 2.5 * self._performance * self._fluid_per_tick

    def preGiveResource(self, resource_type: str, amount: float) -> float:
        if resource_type != self._resource_type:
            return 0.
        if amount < 0:
            return 0.

        # The closer you get to the max, the less it will accept.
        if self._max_storage is not None and self._max_storage * 0.5 <= self._amount + amount:
            storage_left = self._max_storage - self._amount
            factor = storage_left / (0.5 * self._max_storage)
            result = enforcePositive(amount * factor)
            return min(amount, result, storage_left)

        return amount


    def update(self, sub_tick_modifier: float = 1) -> None:
        # First, we store the resources other nodes *gave* us (these are already added!)
        #resource_already_added = self._resources_received_this_tick.get(self._resource_type, 0)

        # Then we check how much resources in total we got this turn (aka; how much after we also requested resources)
        super().update(sub_tick_modifier)
        resource_available = self.getResourceAvailableThisTick(self._resource_type)

        # Now we can figure out how much we really have right now.
        self._amount = self._amount + resource_available
        resources_to_distribute = min(self._fluid_per_tick * self.performance * sub_tick_modifier, self._amount)
        resources_left = self._amount - resources_to_distribute

        # Then we try to give as much away as possible.
        resources_left_after_distribution = self._provideResourceToOutgoingConnections(self._resource_type, resources_to_distribute)

        self._resources_provided_this_tick[self._resource_type] += enforcePositive(resources_to_distribute - resources_left_after_distribution)

        self._amount = resources_left_after_distribution + resources_left

    def postUpdate(self) -> None:
        super().postUpdate()
        # This is done in the post update to ensure that it also takes resources taken by other nodes into account.
        # We can't do this in the update, because other nodes might be updated later.
        self._updateResourceRequiredPerTick()