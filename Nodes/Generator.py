from math import sqrt

from Nodes.Node import Node, modifiable_property
from Nodes.Constants import COMBUSTION_HEAT, WEIGHT_PER_UNIT
from Nodes.Util import enforcePositive


class Generator(Node):
    """
    A generator is a node that can accept fuel, which it will convert into energy.
    Since it burns the fuel, a fair amount of heat is produced in this process. In order to cool it, it can also accept
    water, which it will use to transfer heat into.
    """
    def __init__(self, node_id: str, fuel_type: str = "fuel", energy_factor: float = 10.0, **kwargs) -> None:
        """
        :param node_id:
        :param fuel_type: What resource should it use as fuel?
        :param energy_factor: How much energy should be produced with one fuel resource?
        :param kwargs:
        """
        # Update the defaults like this so that the actual property can be set by base class
        defaults = {"temperature_efficiency": 0.5,
                    "min_performance": 0.5,
                    "max_performance": 2,
                    "weight": 8000,
                    "surface_area": 8,
                    "heat_convection_coefficient": 20,
                    "max_safe_temperature": 400,
                    "performance_change_factor": 4,
                    "usage_damage_factor": 0.16}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        # Some sanity checking.
        if COMBUSTION_HEAT[fuel_type] == 0:
            raise ValueError("The provided fuel type [{fuel_type}] can't be burned!".format(fuel_type = fuel_type))

        self._fuel_type = fuel_type
        self._energy_factor = energy_factor
        self._resources_required_per_tick[fuel_type] = 1
        self._optional_resources_required_per_tick["water"] = 250

        self._resources_left_over["energy"] = 0

        self._use_temperature_dependant_effectiveness_factor = True

        self._description = f"This device accepts fuel and converts it to energy, generating large amounts of " \
                            "heat in the process. As such, it also accepts (and subsequently outputs) water to help" \
                            " with cooling down. Generators require quite some time to start (and stop) producing " \
                            "power. This is caused by their high Performance Change Factor and by the fact that " \
                            "their output is temperature dependant. A generator can be kickstarted faster by " \
                            "setting the performance higher than is needed for some time, as this makes it heat up " \
                            "faster. This is a tricky thing to do however, as it's easy to forget to turn it down " \
                            "again once it reached it's ideal temperature."

        self._providable_resources.add("energy")
        self._providable_resources.add("water")

        self._tags.append("mechanical")
        self._tags.append("fuel")

    @modifiable_property
    def temperature_efficiency(self):
        # A damaged generator starts burning fuel less efficient (making it run more hot!)
        health_factor = self._getHealthEffectivenessFactor()
        result = self._temperature_efficiency * (2 - health_factor)
        return result

    def _updateResourceRequiredPerTick(self) -> None:
        """
        If there were resources left over, we should request less resources next time round.
        """
        energy_left = self._resources_left_over["energy"]
        self._resources_required_per_tick[self._fuel_type] = self._performance * enforcePositive(self._original_resources_required_per_tick[self._fuel_type] * self.health_effectiveness_factor - (energy_left / self._energy_factor))

        water_left = self._resources_left_over.get("water", 0)
        self._optional_resources_required_per_tick["water"] = self._performance * enforcePositive(self._original_optional_resources_required_per_tick["water"] * self.health_effectiveness_factor - water_left)

    def update(self, sub_tick_modifier: float = 1) -> None:
        super().update(sub_tick_modifier)

        fuel_gained = self.getResourceAvailableThisTick(self._fuel_type)

        energy_produced = fuel_gained * self.effectiveness_factor * self._energy_factor

        self._resources_produced_this_tick["energy"] += energy_produced

        energy_available = energy_produced + self._resources_left_over["energy"]

        # Attempt to "get rid" of the energy by offering it to connected sources.
        energy_left = self._provideResourceToOutgoingConnections("energy", energy_available)

        # It's entirely possible that no energy was generated this turn, but a bunch of energy was provided (since there
        # was some energy left over from the last tick!)
        self._resources_provided_this_tick["energy"] += enforcePositive(energy_available - energy_left)

        # The amount of fuel we used is equal to the energy we produced. Depending on that, the generator produces heat
        heat_produced = fuel_gained * COMBUSTION_HEAT[self._fuel_type] * WEIGHT_PER_UNIT[self._fuel_type] * self.temperature_efficiency
        self.addHeat(heat_produced)

        # Same thing for the water. Check how much water we have.
        water_available = self.getResourceAvailableThisTick("water")
        # And try to get rid of some water
        water_left = self._provideResourceToOutgoingConnections("water", water_available)

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over["water"] = water_left

        self._resources_provided_this_tick["water"] += enforcePositive(water_available - water_left)

        self._resources_left_over["energy"] = energy_left
