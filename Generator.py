from Node import Node


class Generator(Node):
    def __init__(self):
        super().__init__()
        self._resources_required_per_tick["fuel"] = 10

    def update(self):
        super().update()

        energy_produced = self._resources_received_this_tick["fuel"]
        outgoing_connections = self.getAllOutgoingConnectionsByType("energy")
        outgoing_connections = sorted(self.getAllOutgoingConnectionsByType("energy"), key=lambda x: x.preGiveResource(energy_produced / len(outgoing_connections)), reverse=True)
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()

            energy_stored = active_connection.giveResource(energy_produced / (len(outgoing_connections) + 1))
            energy_produced -= energy_stored

        # TODO: What to do with leftovers?