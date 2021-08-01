from Nodes.Node import Node


class ConverterNode(Node):
    def __init__(self, node_id: str, input_resource: str, output_resource: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)
        self._input_resource = input_resource
        self._resources_required_per_tick[input_resource] = 10
        self._output_resource = output_resource

    def update(self, sub_tick_modifer: float = 1) -> None:
        super().update(sub_tick_modifer)
        resource_received = self.getResourceAvailableThisTick(self._input_resource, sub_tick_modifer)
        resources_left = self._provideResourceToOutgoingConnections(self._output_resource, resource_received)

        print(self.getId(), "resources left", resources_left)
        if self._output_resource not in self._resources_produced_this_tick:
            self._resources_produced_this_tick[self._output_resource] = 0
        self._resources_produced_this_tick[self._output_resource] += resource_received
        if self._output_resource not in self._resources_provided_this_tick:
            self._resources_provided_this_tick[self._output_resource] = 0
        self._resources_provided_this_tick[self._output_resource] += resource_received - resources_left

