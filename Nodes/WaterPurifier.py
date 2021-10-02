from Nodes.Node import Node
from Nodes.Util import enforcePositive


class WaterPurifier(Node):
    """
    A water purifier accepts dirty water & oxygen, which it converts into clean water & waste.

    When it gets damaged, it will start requesting less resources (and thus decrease it's output)
    """

    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)
        self._optional_resources_required_per_tick["oxygen"] = 140
        self._resources_required_per_tick["dirty_water"] = 10

        self._waste_oxygen_conversion_rate = 28  # 280 oxygen is needed to convert 1 extra dirty water
        self._animal_waste_per_liter_dirty_water = 0.1
        self._tags.append("mechanical")

    def _updateResourceRequiredPerTick(self) -> None:
        """
        If there were resources left over, we should request less resources next time round.
        """
        resources_left_factor = 1 - max(self._resources_left_over["animal_waste"] * 10, self._resources_left_over["water"]) / (10 * self.effectiveness_factor)

        self._optional_resources_required_per_tick["oxygen"] = enforcePositive(self._original_optional_resources_required_per_tick["oxygen"]
                                                          * self.effectiveness_factor * resources_left_factor) * self.performance

        self._resources_required_per_tick["dirty_water"] = enforcePositive(
            self._original_resources_required_per_tick["dirty_water"] * self.effectiveness_factor * resources_left_factor)  * self.performance

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        oxygen_available = self.getResourceAvailableThisTick("oxygen")

        dirty_water_available = self.getResourceAvailableThisTick("dirty_water")
        self._markResourceAsDestroyed("dirty_water", dirty_water_available)
        self._markResourceAsDestroyed("oxygen", oxygen_available)

        # Half of the production can be done without using oxygen.
        dirty_water_converted_for_free = min(dirty_water_available, self._original_resources_required_per_tick["dirty_water"] * sub_tick_modifier * self.performance * self.effectiveness_factor / 2)
        # Now we know how much dirty water we can convert as a bonus
        dirty_water_converted_oxygen = enforcePositive(dirty_water_available - dirty_water_converted_for_free)

        # Now figure out how much oxygen we could spend on the "extra" water
        max_oxygen_required = dirty_water_converted_oxygen * self._waste_oxygen_conversion_rate

        oxygen_required = min(max_oxygen_required, oxygen_available)
        dirty_water_converted_oxygen = 1 / self._waste_oxygen_conversion_rate * oxygen_required
        dirty_water_converted_total = dirty_water_converted_for_free + dirty_water_converted_oxygen

        total_waste_converted = dirty_water_converted_total * self._animal_waste_per_liter_dirty_water
        self._markResourceAsCreated("water", dirty_water_converted_total)
        self._markResourceAsCreated("animal_waste", total_waste_converted)

        self._resources_left_over["oxygen"] = oxygen_available - oxygen_required
        self._resources_left_over["dirty_water"] = dirty_water_available - dirty_water_converted_total
        self._markResourceAsCreated("dirty_water", self._resources_left_over["dirty_water"])
        self._markResourceAsCreated("oxygen", self._resources_left_over["oxygen"])

        # Ensure that we also check how much we had left from the last turn
        clean_water_available = dirty_water_converted_total + self._resources_left_over.get("water", 0)
        waste_available = total_waste_converted + self._resources_left_over.get("animal_waste", 0)

        # Attempt to distribute the resources.
        clean_water_left = self._provideResourceToOutgoingConnections("water", clean_water_available)
        waste_left = self._provideResourceToOutgoingConnections("animal_waste", waste_available)

        # Update the data for bookkeeping
        clean_water_provided = enforcePositive(clean_water_available - clean_water_left)
        waste_provided = enforcePositive(waste_available - waste_left)
        self._resources_produced_this_tick["water"] += dirty_water_converted_total
        self._resources_produced_this_tick["animal_waste"] += total_waste_converted

        self._resources_provided_this_tick["water"] += clean_water_provided
        self._resources_provided_this_tick["animal_waste"] += waste_provided

        # Remember how much we couldn't store anywhere.
        self._resources_left_over["water"] = clean_water_left
        self._resources_left_over["animal_waste"] = waste_left
