from Nodes.Node import Node


class HydroponicsBay(Node):
    """

    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        # TODO: This still needs to be tweaked.
        self._resources_required_per_tick["water"] = 10
        self._resources_required_per_tick["energy"] = 10

    def update(self) -> None:
        super().update()
        # Get the resources we asked for!
        water_available = self.getResourceAvailableThisTick("water")
        energy_available = self.getResourceAvailableThisTick("energy")

        oxygen_produced = min(water_available, energy_available)

        oxygen_left = self._provideResourceToOutogingConnections("oxygen", oxygen_produced)

        self._resources_left_over["oxygen"] = oxygen_left

        oxygen_provided = max(self._resources_received_this_tick["oxygen"] - oxygen_left, 0)
        self._resources_produced_this_tick["oxygen"] = oxygen_provided
