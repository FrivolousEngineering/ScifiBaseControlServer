from Node import Node
import matplotlib.pyplot as plt


class NodeGraph:
    def __init__(self, node: Node):
        self._node = node
        self._node.postUpdateCalled.connect(self._update)

        #self._resources_requested_history = {}
        self._resources_gained_history = {}
        self._num_ticks_stored = 0
        for resource_type in self._node.getResourcesRequiredPerTick():
            self._resources_gained_history[resource_type] = []
            #self._resources_requested_history[resource_type] = []

    def _update(self, _):
        self._num_ticks_stored += 1
        resources_received = self._node.getResourcesReceivedThisTick()
        for resource_type in self._node.getResourcesRequiredPerTick():
            self._resources_gained_history[resource_type].append(resources_received[resource_type])

    def showGraph(self):
        labels = [str(num) for num in range(0, self._num_ticks_stored)]
        for resource_type, data in self._resources_gained_history.items():
            plt.bar(labels, data, label = resource_type)

        plt.xlabel("Ticks")
        plt.ylabel("Amount")
        plt.title("Resources gained by %s" % self._node.getId())
        plt.legend()
        plt.show()