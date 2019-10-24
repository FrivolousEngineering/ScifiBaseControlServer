from Node import Node
import matplotlib.pyplot as plt


class NodeGraph:
    def __init__(self, node: Node):
        self._node = node
        self._node.postUpdateCalled.connect(self._update)

        #self._resources_requested_history = {}
        self._resources_produced_history = {}
        self._resources_gained_history = {}
        self._num_ticks_stored = 0
        self._temperature_history = []
        for resource_type in self._node.getResourcesRequiredPerTick():
            self._resources_gained_history[resource_type] = []
            #self._resources_requested_history[resource_type] = []

    def _update(self, _):
        self._num_ticks_stored += 1
        self._temperature_history.append(self._node.temperature)
        resources_received = self._node.getResourcesReceivedThisTick()
        resources_produced = self._node.getResourcesProducedThisTick()
        for resource_type in self._node.getResourcesRequiredPerTick():
            self._resources_gained_history[resource_type].append(resources_received[resource_type])
        for resource_type in self._node.getResourcesProducedThisTick():
            if resource_type not in self._resources_produced_history:
                self._resources_produced_history[resource_type] = []
            self._resources_produced_history[resource_type].append(resources_produced[resource_type])

    def showGraph(self):
        labels = [str(num) for num in range(0, self._num_ticks_stored)]

        plt.bar(labels, self._temperature_history, label = "Temperature")
        for resource_type, data in self._resources_gained_history.items():
            plt.bar(labels, data, label = resource_type + " used")

        for resource_type, data in self._resources_produced_history.items():
            plt.bar(labels, data, label=resource_type + " produced")
        plt.xlabel("Ticks")
        plt.ylabel("Amount")
        plt.title("Resources flow of %s" % self._node.getId())
        plt.legend()
        plt.show()