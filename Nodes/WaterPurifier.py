from Nodes.Node import Node
from Nodes.Util import enforcePositive


class WaterPurifier(Node):
    """
    A water purifier accepts dirty water & oxygen, which it converts into clean water & waste.

    When it gets damaged, it will start requesting less resources (and thus decrease it's output)
    """

    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id)
        self._optional_resources_required_per_tick["oxygen"] = 10
        self._resources_required_per_tick["dirty_water"] = 10

        self._original_resources_required_per_tick = self._resources_required_per_tick.copy()
        self._optional_original_resources_required_per_tick = self._optional_resources_required_per_tick.copy()

        self._waste_oxygen_conversion_rate = 2  # Two oxygen is required to convert one waste

    def _updateResourceRequiredPerTick(self) -> None:
        resources_left = max(self._resources_left_over["waste"], self._resources_left_over["water"])
        self._optional_resources_required_per_tick["oxygen"] = enforcePositive(self._optional_original_resources_required_per_tick["oxygen"]
                                                          * self.effectiveness_factor - resources_left)

        self._resources_required_per_tick["dirty_water"] = enforcePositive(
            self._original_resources_required_per_tick["dirty_water"] * self.effectiveness_factor - resources_left)

    def update(self) -> None:
        super().update()

        oxygen_available = self.getResourceAvailableThisTick("oxygen")

        dirty_water_available = self.getResourceAvailableThisTick("dirty_water")

        # Half of the production can be done without using oxygen.
        dirty_water_converted_for_free = enforcePositive(dirty_water_available - self._original_resources_required_per_tick["dirty_water"] / 2)

        # Now we know how much dirty water we can convert as a bonus
        dirty_water_converted_oxygen = enforcePositive(dirty_water_available - dirty_water_converted_for_free)

        # Now figure out how much oxygen we could spend on the "extra" water
        max_oxygen_required = dirty_water_converted_oxygen * self._waste_oxygen_conversion_rate

        oxygen_required = min(max_oxygen_required, oxygen_available)
        dirty_water_converted_oxygen = 1 / self._waste_oxygen_conversion_rate * oxygen_required
        dirty_water_converted_total = dirty_water_converted_for_free + dirty_water_converted_oxygen

        self._resources_left_over["oxygen"] = oxygen_available - oxygen_required
        self._resources_left_over["dirty_water"] = dirty_water_available - dirty_water_converted_total

        # Ensure that we also check how much we had left from the last turn
        clean_water_available = dirty_water_converted_total + self._resources_left_over.get("water", 0)
        waste_available = dirty_water_converted_total + self._resources_left_over.get("waste", 0)

        # Attempt to distribute the resources.
        clean_water_left = self._provideResourceToOutgoingConnections("water", clean_water_available)
        waste_left = self._provideResourceToOutgoingConnections("waste", waste_available)

        # Update the data for bookkeeping
        clean_water_provided = enforcePositive(clean_water_available - clean_water_left)
        waste_provided = enforcePositive(waste_available - waste_left)
        self._resources_produced_this_tick["water"] = clean_water_provided
        self._resources_produced_this_tick["waste"] = waste_provided

        # Remember how much we couldn't store anywhere.
        self._resources_left_over["water"] = clean_water_left
        self._resources_left_over["waste"] = waste_left

        # Based on what happened last turn, we should potentially ask for a bit less.
        self._updateResourceRequiredPerTick()
