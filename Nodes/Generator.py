from Nodes.Node import Node
from Nodes.Constants import COMBUSTION_HEAT


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
        super().__init__(node_id, **kwargs)

        # Some sanity checking.
        if COMBUSTION_HEAT[fuel_type] == 0:
            raise ValueError("The provided fuel type [{fuel_type} can't be burned!]".format(fuel_type = fuel_type))

        self._fuel_type = fuel_type
        self._energy_factor = energy_factor
        self._resources_required_per_tick[fuel_type] = 10
        self._resources_required_per_tick["water"] = 250

        self._min_performance = 0.5
        self._max_performance = 2

        # How (in)efficient is the generator in converting the fuel it gets into heat?
        # An efficiency of 1 means that no heat is produced. An efficiency of 0 means that all heat of burning it
        # is transformed into heat.
        self._efficiency = 0.5

        self._max_safe_temperature = 500

        self._weight = 2000
        self._description = "This device accepts {fuel_type} and converts it to energy, generating large amounts of" \
                            "heat in the process. As such, it also accepts (and subsequently outputs) water to help" \
                            "with cooling down.".format(fuel_type = fuel_type)

    def update(self) -> None:
        super().update()

        fuel_gained = self.getResourceAvailableThisTick(self._fuel_type)

        energy_available = fuel_gained * self.effectiveness_factor * self._energy_factor

        # Attempt to "get rid" of the energy by offering it to connected sources.
        energy_left = self._provideResourceToOutogingConnections("energy", energy_available)

        # So, every energy that we didn't give away also means that didn't actually result in fuel being burnt.
        # That's why we put whatever is left back into the fuel "reservoir"
        fuel_left = self.inverted_effectiveness_factor * energy_left
        self._resources_left_over[self._fuel_type] = fuel_left

        # We specifically use what is in the received dict (instead of the energy_available), because we want to
        # know how much was generated (and the resources available also takes leftovers into account)
        self._resources_produced_this_tick["energy"] = max(energy_available - energy_left, 0)

        # The amount of fuel we used is equal to the energy we produced. Depending on that, the generator produces heat
        inefficiency = 1.0 - self._efficiency
        heat_produced = (fuel_gained - fuel_left) * COMBUSTION_HEAT[self._fuel_type] * inefficiency
        self.addHeat(heat_produced)

        # Same thing for the water. Check how much water we have.
        water_available = self.getResourceAvailableThisTick("water")

        # And try to get rid of some water
        water_left = self._provideResourceToOutogingConnections("water", water_available)

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over["water"] = water_left
        self._resources_produced_this_tick["water"] = max(self._resources_received_this_tick["water"] - water_left, 0)
