from Nodes.Node import Node
from Nodes.Util import enforcePositive


class HydroponicsBay(Node):
    """
    The hydroponics bay produces oxygen, and requires water & energy to do so.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        # TODO: This still needs to be tweaked.
        self._resources_required_per_tick["water"] = 100
        self._resources_required_per_tick["energy"] = 5

        self._optional_resources_required_per_tick["animal_waste"] = 5

        self._use_temperature_dependant_effectiveness_factor = True
        self._heat_convection_coefficient = 1
        self._optimal_temperature = 308.15
        self._optimal_temperature_range = 10

    def update(self) -> None:
        super().update()
        # Get the resources we asked for!
        water_available = self.getResourceAvailableThisTick("water")
        energy_available = self.getResourceAvailableThisTick("energy")
        animal_waste_available = self.getResourceAvailableThisTick("animal_waste")
        # We generate 1 oxygen per 1 water and energy we got.
        # The water is likely to be *much* higher, since it accepts way more so it can function to keep it self
        # at the right temperature.
        oxygen_produced = min(water_available, energy_available)

        self._resources_left_over["water"] = water_available - oxygen_produced
        self._resources_left_over["energy"] = energy_available - oxygen_produced
        oxygen_produced *= self.effectiveness_factor

        oxygen_left = self._provideResourceToOutgoingConnections("oxygen", oxygen_produced)

        self._resources_left_over["water"] += oxygen_left * self.inverted_effectiveness_factor
        self._resources_left_over["energy"] += oxygen_left * self.inverted_effectiveness_factor

        oxygen_provided = enforcePositive(oxygen_produced - oxygen_left)
        self._resources_produced_this_tick["oxygen"] = oxygen_provided

        self._resources_left_over["water"] = self._provideResourceToOutgoingConnections("water", self._resources_left_over["water"])

        # All the animal_waste we get is consumed (also makes it a bit more simple...)
        # Getting enough waste means that it produces twice as much. Boom.
        # TODO: Hacked this in for a bit.
        plants_produced = oxygen_produced * (1 + animal_waste_available / self._optional_resources_required_per_tick["animal_waste"])

        self._provideResourceToOutgoingConnections("plants", plants_produced)

