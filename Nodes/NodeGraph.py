import matplotlib.pyplot as plt  # type: ignore
from Nodes.Constants import BAR_COLOR

from Nodes.NodeHistory import NodeHistory


class NodeGraph:

    def __init__(self, node_history: NodeHistory) -> None:
        self._node_history = node_history

    def createGraph(self) -> None:
        num_ticks_stored = self._node_history.getNumTicksStored()

        plt.style.use('ggplot')
        ax1 = plt.subplot(3, 1, 1)
        current_bar_width = 0.
        labels = [num + current_bar_width for num in range(0, num_ticks_stored)]
        plt.bar(labels, self._node_history.getTemperatureHistory(), label="Temperature")
        plt.ylabel("Degrees Kelvin")
        #plt.legend()

        plt.subplot(3, 1, 2, sharex=ax1)
        for resource_type, data in self._node_history.getResourcesGainedHistory().items():
            labels = [num + current_bar_width for num in range(0, num_ticks_stored)]
            plt.bar(labels, data, label=resource_type.title(),
                    width=1 / (len(self._node_history.getResourcesGainedHistory()) + 1), color=BAR_COLOR[resource_type])
            current_bar_width += 1 / len(self._node_history.getResourcesGainedHistory())
        #plt.legend()
        plt.ylabel("Used")

        plt.subplot(3, 1, 3, sharex=ax1)
        current_bar_width = 0
        for resource_type, data in self._node_history.getResourcesProducedHistory().items():
            labels = [num + current_bar_width for num in range(0, num_ticks_stored)]
            plt.bar(labels, data, label=resource_type.title(),
                    width=1 / (len(self._node_history.getResourcesProducedHistory().items()) + 1),
                    color=BAR_COLOR[resource_type])
            current_bar_width += 1 / len(self._node_history.getResourcesProducedHistory().items())

        plt.xlabel("Ticks")
        plt.ylabel("Produced")
        plt.title("Resources flow of %s" % self._node_history.getNode().getId())
        #plt.legend()

    def storeGraph(self) -> None:
        self.createGraph()
        plt.savefig("graphs/%s.png" % self._node_history.getNode().getId())
        plt.close()

    def showGraph(self) -> None:
        self.createGraph()
        plt.show()
