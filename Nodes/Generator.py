from Nodes.Node import Node
from Nodes.Constants import COMBUSTION_HEAT


class Generator(Node):
    """
    A generator is a node that can accept fuel, which it will convert into energy.
    Since it burns the fuel, a fair amount of heat is produced in this process. In order to cool it, it can also accept
    water, which it will use to transfer heat into.
    """
    def __init__(self, node_id: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)
        self._resources_required_per_tick["fuel"] = 10
        self._resources_required_per_tick["water"] = 500

        # How (in)efficient is the generator in converting the fuel it gets into heat?
        # An efficiency of 1 means that no heat is produced. An efficiency of 0 means that all heat of burning it
        # is transformed into heat.
        self._efficiency = 0.5

        self._max_safe_temperature = 500

    def update(self) -> None:
        super().update()

        fuel_gained = self.getResourceAvailableThisTick("fuel")

        # A generator creates 1 energy per fuel that it gets. Yay!
        energy_available = fuel_gained * self.effectiveness_factor

        # Attempt to "get rid" of the energy by offering it to connected sources.
        energy_left = self._provideResourceToOutogingConnections("energy", energy_available)

        # So, every energy that we didn't give away also means that didn't actually result in fuel being burnt.
        # That's why we put whatever is left back into the fuel "reservoir"
        fuel_left = self.inverted_effectiveness_factor * energy_left
        self._resources_left_over["fuel"] = fuel_left

        # We specifically use what is in the received dict (instead of the energy_available), because we want to
        # know how much was generated (and the resources available also takes leftovers into account)
        self._resources_produced_this_tick["energy"] = max(energy_available - energy_left, 0)

        # The amount of fuel we used is equal to the energy we produced. Depending on that, the generator produces heat
        inefficiency = 1.0 - self._efficiency
        heat_produced = (fuel_gained - fuel_left) * COMBUSTION_HEAT["fuel"] * inefficiency
        self.addHeat(heat_produced)

        # Same thing for the water. Check how much water we have.
        water_available = self.getResourceAvailableThisTick("water")

        # And try to get rid of some water
        water_left = self._provideResourceToOutogingConnections("water", water_available)

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over["water"] = water_left
        self._resources_produced_this_tick["water"] = max(self._resources_received_this_tick["water"] - water_left, 0)
