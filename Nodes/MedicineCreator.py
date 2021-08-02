from Nodes.Node import Node
from Nodes.Util import enforcePositive


class MedicineCreator(Node):
    """
    The medicine creator converts raw plant oil, energy and water into medicine
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        # TODO: This still needs to be tweaked.
        self._resources_required_per_tick["water"] = 5
        self._resources_required_per_tick["energy"] = 5
        self._resources_required_per_tick["plant_oil"] = 5

        # It doesn't need the extra water, it just uses it for temperature purposes
        self._optional_resources_required_per_tick["water"] = 25

        self._use_temperature_dependant_effectiveness_factor = True
        self._heat_convection_coefficient = 1
        self._optimal_temperature = 308.15
        self._optimal_temperature_range = 10

        self._heat_per_medicine_created = 100

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)
        # Get the resources we asked for!
        water_available = self.getResourceAvailableThisTick("water")
        energy_available = self.getResourceAvailableThisTick("energy")
        plant_oil_available = self.getResourceAvailableThisTick("animal_waste")

        medicine_produced = min(water_available, energy_available, plant_oil_available)

        self._resources_left_over["water"] = water_available - medicine_produced
        self._resources_left_over["energy"] = energy_available - medicine_produced
        self._resources_left_over["plant_oil"] = plant_oil_available - medicine_produced

        medicine_produced *= self.effectiveness_factor
        self._resources_produced_this_tick["medicine"] += medicine_produced

        # Attempt to get rid of the medicine
        medicine_left = self._provideResourceToOutgoingConnections("medicine", medicine_produced)

        # if that failed, we didn't use some of the resources we got
        self._resources_left_over["water"] += medicine_left * self.inverted_effectiveness_factor
        self._resources_left_over["energy"] += medicine_left * self.inverted_effectiveness_factor
        self._resources_left_over["plant_oil"] = medicine_left * self.inverted_effectiveness_factor

        medicine_provided = enforcePositive(medicine_produced - medicine_left)
        self._resources_provided_this_tick["medicine"] += medicine_provided

        heat_produced = medicine_provided * self._heat_per_medicine_created * self.temperature_efficiency
        self.addHeat(heat_produced)