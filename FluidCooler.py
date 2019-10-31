from ResourceStorage import ResourceStorage


class FluidCooler(ResourceStorage):
    def __init__(self, node_id: str, resource_type: str, fluid_per_tick: float):
        super().__init__(node_id, resource_type, 0, fluid_per_tick)
        self._surface_area = 8
        self._heat_emissivity = 0.9

    def update(self):
        super().update()

        resource_left = self.getResourceAvailableThisTick(self._resource_type)
        outgoing_connections = self.getAllOutgoingConnectionsByType(self._resource_type)
        outgoing_connections = sorted(self.getAllOutgoingConnectionsByType(self._resource_type),
                                      key=lambda x: x.preGiveResource(resource_left / len(outgoing_connections)),
                                      reverse=True)
        while len(outgoing_connections):
            active_connection = outgoing_connections.pop()
            resource_stored = active_connection.giveResource(resource_left / (len(outgoing_connections) + 1))
            resource_left -= resource_stored
            self._amount -= resource_stored

        # Some amount could not be dumped, so this means we will just request less next tick.
        self._resources_left_over[self._resource_type] = resource_left