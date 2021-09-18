from Nodes.Constants import SPECIFIC_HEAT, WEIGHT_PER_UNIT
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

        self._optional_resources_required_per_tick["animal_waste"] = 5
        # It doesn't need the extra water, it just uses it for temperature purposes
        self._optional_resources_required_per_tick["water"] = 95

        self._use_temperature_dependant_effectiveness_factor = True
        self._heat_convection_coefficient = kwargs.get("heat_convection_coefficient", 1.)  # type: float
        self._optimal_temperature = kwargs.get("optimal_temperature", 308.15)  # type: float
        self._optimal_temperature_range = kwargs.get("optimal_temperature_range", 10) # type: float

        self._weight = kwargs.get("weight", 2000)  # type: float

        self._tags.append("plant")

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)
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

        self._resources_produced_this_tick["oxygen"] += oxygen_produced

        oxygen_left = self._provideResourceToOutgoingConnections("oxygen", oxygen_produced)

        self._resources_left_over["water"] += oxygen_left * self.inverted_effectiveness_factor
        self._resources_left_over["energy"] += oxygen_left * self.inverted_effectiveness_factor

        oxygen_provided = enforcePositive(oxygen_produced - oxygen_left)

        self._resources_provided_this_tick["oxygen"] += oxygen_provided

        water_left = self._provideResourceToOutgoingConnections("water", self._resources_left_over["water"])
        water_provided_this_tick = enforcePositive(self._resources_left_over["water"] - water_left)
        self._resources_provided_this_tick["water"] += water_provided_this_tick
        self._resources_left_over["water"] = water_left


        # All the animal_waste we get is consumed (also makes it a bit more simple...)
        # Getting enough waste means that it produces twice as much. Boom.
        # TODO: Hacked this in for a bit.
        plants_produced = oxygen_produced * (1 + animal_waste_available / (self._optional_resources_required_per_tick["animal_waste"] * sub_tick_modifier))

        # Some water was destroyed:
        amount_of_water_used_this_tick = self._resources_received_this_sub_tick.get("water",
                                                                                    0) - water_provided_this_tick
        self._markResourceAsDestroyed("water", amount_of_water_used_this_tick)
        self._markResourceAsDestroyed("animal_waste", animal_waste_available)
        self._markResourceAsCreated("oxygen", oxygen_produced)
        self._markResourceAsCreated("plants", plants_produced)

        self._resources_produced_this_tick["plants"] += plants_produced
        self._resources_provided_this_tick["plants"] += plants_produced - self._provideResourceToOutgoingConnections("plants", plants_produced)
