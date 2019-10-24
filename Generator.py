from Node import Node


class Generator(Node):
    def __init__(self, node_id: str) -> None:
        super().__init__(node_id)
        self._resources_required_per_tick["fuel"] = 10
        self._resources_required_per_tick["water"] = 10

    def update(self):
        super().update()

        energy_produced = self._resources_received_this_tick["fuel"]

        outgoing_connections = self.getAllOutgoingConnectionsByType("energy")
        outgoing_connections = sorted(self.getAllOutgoingConnectionsByType("energy"), key=lambda x: x.preGiveResource(energy_produced / len(outgoing_connections)), reverse=True)
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()

            energy_stored = active_connection.giveResource(energy_produced / (len(outgoing_connections) + 1))
            energy_produced -= energy_stored
        self._resources_produced_this_tick["energy"] = self._resources_received_this_tick["fuel"] - energy_produced

        water_produced = self._resources_received_this_tick["water"]
        outgoing_connections = self.getAllOutgoingConnectionsByType("water")
        outgoing_connections = sorted(self.getAllOutgoingConnectionsByType("water"),
                                      key=lambda x: x.preGiveResource(water_produced / len(outgoing_connections)),
                                      reverse=True)
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()

            water_stored = active_connection.giveResource(water_produced / (len(outgoing_connections) + 1))
            water_produced -= water_stored


        heat_produced = self._resources_received_this_tick["fuel"] * 120
        self.addHeat(heat_produced)

        self._resources_produced_this_tick["water"] =self._resources_received_this_tick["water"] - water_produced
        # TODO: What to do with leftovers?