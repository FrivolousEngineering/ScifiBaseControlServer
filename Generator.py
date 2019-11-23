from Node import Node
from Constants import combustion_heat


class Generator(Node):
    """
    A generator is a node that can accept fuel, which it will convert into energy.
    Since it burns the fuel, a fair amount of heat is produced in this process. In order to cool it, it can also accept
    water, which it will use to transfer heat into.
    """
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id)
        self._resources_required_per_tick["fuel"] = 10
        self._resources_required_per_tick["water"] = 10

    def update(self) -> None:
        super().update()

        # A generator creates 1 energy per fuel that it gets. Yay!
        energy_produced = self.getResourceAvailableThisTick("fuel")
        # Attempt to "get rid" of the energy by offering it to connected sources.
        energy_left = self._provideResourceToOutogingConnections("energy", energy_produced)

        # So, every energy that we didn't give away also means that didn't actually result in fuel being burnt.
        # That's why we put whatever is left back into the fuel "reservoir"
        self._resources_left_over["fuel"] = energy_left
        self._resources_produced_this_tick["energy"] = max(self._resources_received_this_tick["fuel"] - energy_left, 0)

        # The amount of fuel we used is equal to the energy we produced. Depending on that, the generator produces heat
        heat_produced = self._resources_produced_this_tick["energy"] * combustion_heat["fuel"]
        self.addHeat(heat_produced)

        # Same thing for the water. Check how much water we have.
        water_available = self.getResourceAvailableThisTick("water")

        # And try to get rid of some water
        water_left = self._provideResourceToOutogingConnections("water", water_available)

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over["water"] = water_left
        self._resources_produced_this_tick["water"] = max(self._resources_received_this_tick["water"] - water_left, 0)