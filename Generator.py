from Node import Node


class Generator(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id)
        self._resources_required_per_tick["fuel"] = 10
        self._resources_required_per_tick["water"] = 10

    def update(self):
        super().update()

        # A generator creates 1 energy per fuel that it gets. Yay!
        energy_left = self.getResourceAvailableThisTick("fuel")

        # Attempt to "get rid" of the energy by offering it to connected sources.
        outgoing_connections = self.getAllOutgoingConnectionsByType("energy")
        outgoing_connections = sorted(self.getAllOutgoingConnectionsByType("energy"), key=lambda x: x.preGiveResource(energy_left / len(outgoing_connections)), reverse=True)
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()
            energy_stored = active_connection.giveResource(energy_left / (len(outgoing_connections) + 1))
            energy_left -= energy_stored

        # So, every energy that we didn't give away also means that didn't actually result in fuel being burnt.
        # That's why we put whatever is left back into the fuel "resevoir"
        self._resources_left_over["fuel"] = energy_left
        self._resources_produced_this_tick["energy"] = max(self._resources_received_this_tick["fuel"] - energy_left, 0)

        # The amount of fuel we used is equal to the energy we produced. Depending on that, the generator produces heat
        heat_produced = self._resources_produced_this_tick["energy"] * 120
        self.addHeat(heat_produced)

        # Same thing for the water. Check how much water we have.
        water_left = self.getResourceAvailableThisTick("water")
        outgoing_connections = self.getAllOutgoingConnectionsByType("water")
        outgoing_connections = sorted(self.getAllOutgoingConnectionsByType("water"),
                                      key=lambda x: x.preGiveResource(water_left / len(outgoing_connections)),
                                      reverse=True)
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()
            water_stored = active_connection.giveResource(water_left / (len(outgoing_connections) + 1))
            water_left -= water_stored

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over["water"] = water_left
        self._resources_produced_this_tick["water"] = max(self._resources_received_this_tick["water"] - water_left, 0)