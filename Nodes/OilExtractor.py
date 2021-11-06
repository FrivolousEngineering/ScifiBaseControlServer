from Nodes.Constants import COMBUSTION_HEAT, WEIGHT_PER_UNIT, SPECIFIC_HEAT
from Nodes.Node import Node, modifiable_property
from Nodes.Util import enforcePositive


class OilExtractor(Node):
    """
    The Oil extractor is a node that creates plant_oil from plants and fuel. It can also accept water for cooling
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)

        self._resources_required_per_tick["fuel"] = 1
        self._resources_required_per_tick["plants"] = 10
        self._optional_resources_required_per_tick["water"] = 250
        self._health = 100
        self._temperature_efficiency = 0.5
        self._weight = 1000
        self._surface_area = 8

        self._fuel_per_plant_ratio = self._resources_required_per_tick["plants"] / self._resources_required_per_tick["fuel"]

        self._description = "This device extracts essential oils from plants. The process requires fuel, but only a part" \
                            "of the fuel provided is used. The contaminated fuel is burned in the process. All fuel that" \
                            "can not be returned is burned as well."

        self._tags.append("mechanical")

    @modifiable_property
    def temperature_efficiency(self):
        # A damaged OilExtractor starts burning fuel less efficient (making it run more hot!)
        health_factor = self._getHealthEffectivenessFactor()
        result = self._temperature_efficiency * (1.5 - health_factor)
        return result

    def _updateResourceRequiredPerTick(self) -> None:
        """
        If there were resources left over, we should request less resources next time round.
        """
        water_left = self._resources_left_over.get("water", 0)
        self._optional_resources_required_per_tick["water"] = self._performance * enforcePositive(self._original_optional_resources_required_per_tick["water"] * self.health_effectiveness_factor - water_left)

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        # Get all the resources that we want
        fuel_available = self.getResourceAvailableThisTick("fuel")
        plants_available = self.getResourceAvailableThisTick("plants")

        water_available = self.getResourceAvailableThisTick("water")

        oil_produced = min(5 * fuel_available, plants_available)

        self._resources_left_over["plants"] = plants_available - oil_produced
        self._resources_left_over["fuel"] = fuel_available - oil_produced / self._fuel_per_plant_ratio

        # If the extractor gets damaged it will start to generate more waste.
        # For every oil that isn't produced, we generate an extra waste.
        # So, if it's running at 75% effiency, we will generate 0.75 oil and 1.25 waste
        waste_produced = oil_produced + (oil_produced - oil_produced * self.effectiveness_factor)
        self._resources_produced_this_tick["waste"] += waste_produced

        oil_produced *= self.effectiveness_factor
        self._resources_produced_this_tick["plant_oil"] += oil_produced

        # Dump the resources produced
        oil_left = self._provideResourceToOutgoingConnections("plant_oil", oil_produced)
        waste_left = self._provideResourceToOutgoingConnections("waste", waste_produced)

        # If we couldn't dump one of our resources, we just produce less.
        max_resource_left = max(oil_left, waste_left)

        # If a part of the resources (oil or waste) could not be dumped, we have more plants/fuel left.
        self._resources_left_over["plants"] += max_resource_left * self.inverted_effectiveness_factor

        self._resources_left_over["fuel"] += max_resource_left / self._fuel_per_plant_ratio * self.inverted_effectiveness_factor

        fuel_used = fuel_available - self._resources_left_over["fuel"]

        # Burn half of the fuel used to actually produce something
        heat_produced = 0.5 * fuel_used * COMBUSTION_HEAT["fuel"] * WEIGHT_PER_UNIT["fuel"] * self.temperature_efficiency

        self.addHeat(heat_produced)

        # Then try to dump half of the fuel that we received back again
        self._resources_left_over["fuel"] += self._provideResourceToOutgoingConnections("fuel", 0.5 * fuel_used)

        # Burn *all* of the fuel that was not used to produce something (or could not be dumped!)
        heat_produced = self._resources_left_over["fuel"] * COMBUSTION_HEAT["fuel"] * WEIGHT_PER_UNIT["fuel"] * self.temperature_efficiency
        self.addHeat(heat_produced)
        self._resources_left_over["fuel"] = 0

        # And try to get rid of some water
        water_left = self._provideResourceToOutgoingConnections("water", water_available)
        water_provided = enforcePositive(water_available - water_left)
        self._resources_provided_this_tick["water"] += water_provided
        self._resources_left_over["water"] = water_left

        oil_provided = enforcePositive(oil_produced - oil_left)
        self._resources_provided_this_tick["plant_oil"] += oil_provided

        waste_provided = enforcePositive(waste_produced - waste_left)
        self._resources_provided_this_tick["waste"] += waste_provided
