from Nodes.Node import Node
from Nodes.Util import enforcePositive


class ConverterNode(Node):
    def __init__(self, node_id: str, input_resource: str, output_resource: str, **kwargs) -> None:
        super().__init__(node_id, **kwargs)
        self._input_resource = input_resource
        self._resources_required_per_tick[input_resource] = 10
        self._output_resource = output_resource

    def update(self, sub_tick_modifer: float = 1) -> None:
        super().update(sub_tick_modifer)
        resource_received = self.getResourceAvailableThisTick(self._input_resource, sub_tick_modifer)

        # Since it's a 1 on 1 conversion, check what we had left from last time
        resources_available = resource_received + self._resources_left_over.get(self._output_resource, 0)

        resources_left = self._provideResourceToOutgoingConnections(self._output_resource, resources_available)

        if self._output_resource not in self._resources_produced_this_tick:
            self._resources_produced_this_tick[self._output_resource] = 0
        self._resources_produced_this_tick[self._output_resource] += resource_received
        if self._output_resource not in self._resources_provided_this_tick:
            self._resources_provided_this_tick[self._output_resource] = 0
        self._resources_provided_this_tick[self._output_resource] += resources_available - resources_left

        self._resources_left_over[self._output_resource] = resources_left
        self._updateResourceRequiredPerTick()

    def _updateResourceRequiredPerTick(self) -> None:
        resources_left = self._resources_left_over[self._output_resource]
        self._resources_required_per_tick[self._input_resource] = self._performance * enforcePositive(self._original_resources_required_per_tick[self._input_resource] * self.health_effectiveness_factor - resources_left)