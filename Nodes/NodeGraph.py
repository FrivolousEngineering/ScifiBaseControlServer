import matplotlib.pyplot as plt  # type: ignore
from Nodes.Constants import BAR_COLOR

from Nodes.NodeHistory import NodeHistory


class NodeGraph(NodeHistory):
    def showGraph(self):
        plt.style.use('ggplot')
        ax1= plt.subplot(3, 1, 1)
        current_bar_width = 0
        labels = [num + current_bar_width for num in range(0, self._num_ticks_stored)]
        plt.bar(labels, self._temperature_history, label = "Temperature")
        plt.ylabel("Degrees Kelvin")
        plt.legend()

        plt.subplot(3, 1, 2, sharex = ax1)
        for resource_type, data in self._resources_gained_history.items():
            labels = [num + current_bar_width for num in range(0, self._num_ticks_stored)]
            plt.bar(labels, data, label = resource_type.title(),
                    width= 1 / (len(self._resources_gained_history.items()) + 1), color = BAR_COLOR[resource_type])
            current_bar_width += 1 / len(self._resources_gained_history.items())
        plt.legend()
        plt.ylabel("Used")

        plt.subplot(3, 1, 3, sharex = ax1)
        current_bar_width = 0
        for resource_type, data in self._resources_produced_history.items():
            labels = [num + current_bar_width for num in range(0, self._num_ticks_stored)]
            plt.bar(labels, data, label=resource_type.title(),
                    width=1 / (len(self._resources_produced_history.items()) + 1), color=BAR_COLOR[resource_type])
            current_bar_width += 1 / len(self._resources_produced_history.items())

        plt.xlabel("Ticks")
        plt.ylabel("Produced")
        plt.title("Resources flow of %s" % self._node.getId())
        plt.legend()
        plt.show()
