from Nodes.Node import Node
from Nodes.Util import enforcePositive


class HydroponicsBay(Node):
    """
    The hydroponics bay produces oxygen, and requires water & energy to do so.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        # TODO: This still needs to be tweaked.
        self._resources_required_per_tick["water"] = 5
        self._resources_required_per_tick["energy"] = 5

        self._use_temperature_dependant_effectiveness_factor = True
        self._heat_convection_coefficient = 1
        self._optimal_temperature = 308.15
        self._optimal_temperature_range = 5

    def update(self) -> None:
        super().update()
        # Get the resources we asked for!
        water_available = self.getResourceAvailableThisTick("water")
        energy_available = self.getResourceAvailableThisTick("energy")

        oxygen_produced = min(water_available, energy_available)

        self._resources_left_over["water"] = water_available - oxygen_produced
        self._resources_left_over["energy"] = energy_available - oxygen_produced
        oxygen_produced *= self.effectiveness_factor
        oxygen_left = self._provideResourceToOutgoingConnections("oxygen", oxygen_produced)

        self._resources_left_over["water"] += oxygen_left * self.inverted_effectiveness_factor
        self._resources_left_over["energy"] += oxygen_left * self.inverted_effectiveness_factor

        oxygen_provided = enforcePositive(oxygen_produced - oxygen_left)
        self._resources_produced_this_tick["oxygen"] = oxygen_provided

        #TODO: Hacked this in for a bit.
        self._provideResourceToOutgoingConnections("plants", oxygen_produced)

