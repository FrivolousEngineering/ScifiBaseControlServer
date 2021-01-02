from math import sqrt

from Nodes.Node import Node, modifiable_property
from Nodes.Constants import COMBUSTION_HEAT
from Nodes.Util import enforcePositive


class Generator(Node):
    """
    A generator is a node that can accept fuel, which it will convert into energy.
    Since it burns the fuel, a fair amount of heat is produced in this process. In order to cool it, it can also accept
    water, which it will use to transfer heat into.
    """
    def __init__(self, node_id: str, fuel_type: str = "fuel", energy_factor: float = 1.0, **kwargs) -> None:
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
                    "heat_convection_coefficient": 20}
        defaults.update(kwargs)
        super().__init__(node_id, **defaults)

        # Some sanity checking.
        if COMBUSTION_HEAT[fuel_type] == 0:
            raise ValueError("The provided fuel type [{fuel_type}] can't be burned!".format(fuel_type = fuel_type))

        self._fuel_type = fuel_type
        self._energy_factor = energy_factor
        self._resources_required_per_tick[fuel_type] = 10
        self._optional_resources_required_per_tick["water"] = 250

        self._resources_left_over["energy"] = 0

        self._original_resources_required_per_tick = self._resources_required_per_tick.copy()
        self._original_optional_resources_required_per_tick = self._optional_resources_required_per_tick.copy()
        self._max_safe_temperature = 400

        self._use_temperature_dependant_effectiveness_factor = True
        self._performance_change_factor = 3

        self._description = "This device accepts {fuel_type} and converts it to energy, generating large amounts of" \
                            "heat in the process. As such, it also accepts (and subsequently outputs) water to help" \
                            "with cooling down."
        self._description = self._description.format(fuel_type = fuel_type)

    @modifiable_property
    def temperature_efficiency(self):
        # A damaged generator starts burning fuel less efficient (making it run more hot!)
        health_factor = self._getHealthEffectivenessFactor()
        result = self._temperature_efficiency * (2 - health_factor)
        return result

    def _updateResourceRequiredPerTick(self) -> None:
        resources_left = self._resources_left_over["energy"]
        self._resources_required_per_tick[self._fuel_type] = self._performance * enforcePositive(self._original_resources_required_per_tick[self._fuel_type] * self.health_effectiveness_factor - resources_left)

    def update(self) -> None:
        super().update()

        fuel_gained = self.getResourceAvailableThisTick(self._fuel_type)

        energy_available = fuel_gained * self.effectiveness_factor * self._energy_factor + self._resources_left_over["energy"]

        # Attempt to "get rid" of the energy by offering it to connected sources.
        energy_left = self._provideResourceToOutgoingConnections("energy", energy_available)

        # We specifically use what is in the received dict (instead of the energy_available), because we want to
        # know how much was generated (and the resources available also takes leftovers into account)
        self._resources_produced_this_tick["energy"] = enforcePositive(energy_available - energy_left)

        # The amount of fuel we used is equal to the energy we produced. Depending on that, the generator produces heat
        heat_produced = fuel_gained * COMBUSTION_HEAT[self._fuel_type] * self.temperature_efficiency
        self.addHeat(heat_produced)

        # Same thing for the water. Check how much water we have.
        water_available = self.getResourceAvailableThisTick("water")

        # And try to get rid of some water
        water_left = self._provideResourceToOutgoingConnections("water", water_available)

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over["water"] = water_left
        self._resources_produced_this_tick["water"] = enforcePositive(self._resources_received_this_tick["water"] - water_left)

        self._resources_left_over["energy"] = energy_left

        # Based on what happened last turn, we should potentially ask for a bit less.
        self._updateResourceRequiredPerTick()
