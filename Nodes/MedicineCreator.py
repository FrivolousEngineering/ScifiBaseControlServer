from Nodes.Node import Node
from Nodes.Util import enforcePositive


class MedicineCreator(Node):
    """
    The medicine creator converts raw plant oil, energy and water into medicine
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {"heat_convection_coefficient": 1,
                    "optimal_temperature": 308.15,
                    "optimal_temperature_range": 10,
                    "usage_damage_factor": 0.15,
                    "performance_change_factor": 2.2}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        # TODO: This still needs to be tweaked.
        self._resources_required_per_tick["water"] = 5
        self._resources_required_per_tick["energy"] = 5
        self._resources_required_per_tick["plant_oil"] = 5

        # It doesn't need the extra water, it just uses it for temperature purposes
        self._optional_resources_required_per_tick["water"] = 25

        self._heat_per_medicine_created = 100

        self._providable_resources.add("medicine")
        self._providable_resources.add("water")

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)
        # Get the resources we asked for!
        water_available = self.getResourceAvailableThisTick("water")
        energy_available = self.getResourceAvailableThisTick("energy")
        plant_oil_available = self.getResourceAvailableThisTick("plant_oil")

        medicine_produced = min(water_available, energy_available, plant_oil_available)
        self._resources_left_over["water"] = water_available - medicine_produced
        self._resources_left_over["energy"] = energy_available - medicine_produced
        self._resources_left_over["plant_oil"] = plant_oil_available - medicine_produced

        medicine_produced *= self.effectiveness_factor

        self._resources_produced_this_tick["medicine"] += medicine_produced

        # Attempt to get rid of the medicine
        medicine_left = self._provideResourceToOutgoingConnections("medicine", medicine_produced)

        # if that failed, we didn't use some of the resources we got
        water_left = medicine_left * self.inverted_effectiveness_factor
        energy_left = medicine_left * self.inverted_effectiveness_factor
        plant_oil_left = medicine_left * self.inverted_effectiveness_factor
        self._resources_left_over["water"] += water_left
        self._resources_left_over["energy"] += energy_left
        self._resources_left_over["plant_oil"] = plant_oil_left

        medicine_provided = enforcePositive(medicine_produced - medicine_left)
        self._resources_provided_this_tick["medicine"] += medicine_provided

        # Heat bookkeeping
        water_used_in_production = enforcePositive(water_available - self._resources_left_over["water"])
        plant_oil_used_in_production = enforcePositive(plant_oil_available - self._resources_left_over["plant_oil"])
        self._markResourceAsDestroyed("water", water_used_in_production)
        self._markResourceAsDestroyed("plant_oil", plant_oil_used_in_production)
        self._markResourceAsCreated("medicine", medicine_produced)

        # Add extra heat for production
        heat_produced = medicine_provided * self._heat_per_medicine_created * self.temperature_efficiency
        self.addHeat(heat_produced)

        # Attempt to get rid of remaining water
        self._resources_left_over["water"] = self._provideResourceToOutgoingConnections("water",
                                                                                        self._resources_left_over[
                                                                                            "water"])

