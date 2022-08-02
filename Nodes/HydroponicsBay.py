from Nodes.Node import Node
from Nodes.Util import enforcePositive


class HydroponicsBay(Node):
    """
    The hydroponics bay produces oxygen, and requires water & energy to do so.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        defaults = {"temperature_efficiency": 0.5,
                    "min_performance": 0.5,
                    "max_performance": 2,
                    "weight": 2000,
                    "optimal_temperature":  308.15,
                    "optimal_temperature_range": 20,
                    "heat_convection_coefficient": 1,
                    "usage_damage_factor": 0.11,
                    "performance_change_factor": 4.3
                    }
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        # TODO: This still needs to be tweaked.
        self._resources_required_per_tick["water"] = 20
        self._resources_required_per_tick["energy"] = 5

        self._optional_resources_required_per_tick["animal_waste"] = 1
        # It doesn't need the extra water, it just uses it for temperature purposes
        self._optional_resources_required_per_tick["water"] = 95

        self._description = "The hydroponics bay grows plants and creates oxygen. When it's provided with animal " \
                            "waste, it can produce plants much faster, but it's not a hard requirement. A part of " \
                            "the water that it receives is used to grow the plants. Most of the water that it " \
                            "accepts is used to regulate the temperature. Every kg of plant mass will produce 187.5 " \
                            "liter of oxygen"

        self._use_temperature_dependant_effectiveness_factor = True
        self._tags.append("plant")

        self._providable_resources.add("water")
        self._providable_resources.add("oxygen")
        self._providable_resources.add("plants")

    def _updateResourceRequiredPerTick(self) -> None:
        # Find the limiting factor for resources that were left over!
        oxygen_factor = 1  # 1 means that all oxygen was provided this tick
        if self._resources_left_over["oxygen"] > 0:
            oxygen_factor = self._resources_provided_this_tick["oxygen"] / self._resources_left_over["oxygen"]

        plant_factor = 1
        if self._resources_left_over["plants"] > 0:
            plant_factor = self._resources_provided_this_tick["plants"] / self._resources_left_over["plants"]

        self._logistics_factor = min(plant_factor, oxygen_factor)

        self._setPerformance(self._performance)

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)
        # Get the resources we asked for!
        water_available = self.getResourceAvailableThisTick("water")
        energy_available = self.getResourceAvailableThisTick("energy")
        animal_waste_available = self.getResourceAvailableThisTick("animal_waste")

        plants_produced_without_awaste = min(water_available, energy_available * 4) * self.effectiveness_factor

        total_plants_produced = plants_produced_without_awaste * (1 + animal_waste_available / (
                    self._optional_resources_required_per_tick["animal_waste"] * sub_tick_modifier))

        oxygen_produced = total_plants_produced * 187.5

        self._resources_produced_this_tick["oxygen"] += oxygen_produced
        self._resources_produced_this_tick["plants"] += total_plants_produced

        oxygen_left = self._provideResourceToOutgoingConnections("oxygen",
                                                                 oxygen_produced + self._resources_left_over["oxygen"])

        plants_left = self._provideResourceToOutgoingConnections("plants",
                                                                 total_plants_produced + self._resources_left_over["plants"])

        oxygen_provided = enforcePositive(oxygen_produced + self._resources_left_over["oxygen"] - oxygen_left)
        plants_provided = enforcePositive(total_plants_produced + self._resources_left_over["plants"] - plants_left)

        self._resources_left_over["oxygen"] = oxygen_left
        self._resources_left_over["plants"] = plants_left

        self._resources_provided_this_tick["oxygen"] += oxygen_provided
        self._resources_provided_this_tick["plants"] += plants_provided

        # Per 1 plant we created, we have destroyed 1 water
        water_used = total_plants_produced

        water_left = water_available - water_used

        self._markResourceAsDestroyed("animal_waste", animal_waste_available)
        self._markResourceAsDestroyed("water", water_used)
        self._markResourceAsCreated("oxygen", oxygen_produced)
        self._markResourceAsCreated("plants", total_plants_produced)

        self._resources_left_over["water"] = self._provideResourceToOutgoingConnections("water", water_left)
        self._resources_provided_this_tick["water"] += water_left - self._resources_left_over["water"]

