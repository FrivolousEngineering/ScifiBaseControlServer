from Nodes.Node import Node


class WaterPurifier(Node):
    """
    A water purifier accepts dirty water & oxygen, which it converts into clean water & waste.

    When it gets damaged, it will start requesting less resources (and thus decrease it's output)
    """

    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id)
        self._resources_required_per_tick["oxygen"] = 10
        self._resources_required_per_tick["dirty_water"] = 10

        self._original_resources_required_per_tick = self._resources_required_per_tick.copy()

    def _updateResourceRequiredPerTick(self) -> None:
        resources_left = max(self._resources_left_over["waste"], self._resources_left_over["water"])

        self._resources_required_per_tick["oxygen"] = max(self._original_resources_required_per_tick["oxygen"]
                                                          * self.effectiveness_factor - resources_left, 0)
        self._resources_required_per_tick["dirty_water"] = max(
            self._original_resources_required_per_tick["dirty_water"] * self.effectiveness_factor - resources_left, 0)

    def update(self) -> None:
        super().update()

        oxygen_available = self.getResourceAvailableThisTick("oxygen")

        dirty_water_available = self.getResourceAvailableThisTick("dirty_water")

        resources_produced = min(oxygen_available, dirty_water_available)

        self._resources_left_over["oxygen"] = oxygen_available - resources_produced
        self._resources_left_over["dirty_water"] = dirty_water_available - resources_produced

        # Ensure that we also check how much we had left from the last turn
        clean_water_available = resources_produced + self._resources_left_over.get("water", 0)
        waste_available = resources_produced + self._resources_left_over.get("waste", 0)

        # Attempt to distribute the resources.
        clean_water_left = self._provideResourceToOutogingConnections("water", clean_water_available)
        waste_left = self._provideResourceToOutogingConnections("waste", waste_available)

        # Update the data for bookkeeping
        clean_water_provided = max(clean_water_available - clean_water_left, 0)
        waste_provided = max(waste_available - waste_left, 0)
        self._resources_produced_this_tick["water"] = clean_water_provided
        self._resources_produced_this_tick["waste"] = waste_provided

        # Remember how much we couldn't store anywhere.
        self._resources_left_over["water"] = clean_water_left
        self._resources_left_over["waste"] = waste_left

        # Based on what happened last turn, we should potentially ask for a bit less.
        self._updateResourceRequiredPerTick()
