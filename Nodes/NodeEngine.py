from threading import RLock
from typing import List, Dict, Any, Optional

from Nodes.Node import Node
from Nodes.NodeFactory import NodeFactory
from Nodes.NodeHistory import NodeHistory
from Nodes.TemperatureHandlers.TemperatureHandler import TemperatureHandler
from Nodes.PerpetualTimer import PerpetualTimer
from Signal import signalemitter, Signal

TICK_INTERVAL = 15


@signalemitter
class NodeEngine:
    """
    The node engine is responsible for handling ticks (a single update) and subsequently ensuring that all nodes in it's
    list get updated. Once this tick is completed, the state is left in such a way that data can be read (eg; What
    nodes got what they wanted, which didn't, etc).
    """

    preUpdateCalled = Signal()
    updateCalled = Signal()
    postUpdateCalled = Signal()
    tickCompleted = Signal()

    def __init__(self) -> None:
        self._nodes = {}  # type: Dict[str, Node]
        self._node_histories = {}  # type: Dict[str, NodeHistory]

        self._update_lock = RLock()

        self._tick_timer = PerpetualTimer(TICK_INTERVAL, self.doTick)

        self._outside_temperature_handler = None  # type: Optional[TemperatureHandler]
        self._tick_count = 0

        # WIP: How many "in between" updates per tick should be done?
        self._sub_ticks = 10

    @property
    def tick_count(self):
        return self._tick_count

    def setOutsideTemperatureHandler(self, temp_handler: TemperatureHandler) -> None:
        self._outside_temperature_handler = temp_handler

    def _updateOutsideTemperature(self) -> None:
        new_temperature = 293.15
        if self._outside_temperature_handler is not None:
            new_temperature = self._outside_temperature_handler.getTemperatureForTick(self._tick_count)

        for node in self.getAllNodes().values():
            node.outside_temp = new_temperature

    def start(self) -> None:
        self._tick_timer.start()

    def stop(self) -> None:
        self._tick_timer.cancel()

    def registerNode(self, node: Node) -> None:
        if node.getId() not in self._nodes:
            self._nodes[node.getId()] = node
            self.preUpdateCalled.connect(node.acquireUpdateLock)
            self.postUpdateCalled.connect(node.releaseUpdateLock)
            self._node_histories[node.getId()] = NodeHistory(node)
            node.ensureSaneValues()
        else:
            raise KeyError("Node must have an unique ID!")

    def getAllNodes(self) -> Dict[str, Node]:
        return self._nodes

    def getNodeById(self, node_id: str) -> Optional[Node]:
        return self._nodes.get(node_id)

    def getNodeHistoryById(self, node_id: str) -> Optional[NodeHistory]:
        return self._node_histories.get(node_id)

    def deserialize(self, serialized: Dict[str, Any]) -> None:
        """
        Load a configuration file and create all the nodes & connections defined in it.
        :param serialized: A Dict that must contain the keys nodes & connections.
        :return:
        """
        self._registerNodesFromConfigurationData(serialized["nodes"])
        self._registerConnectionsFromConfigurationData(serialized["connections"])

    def _registerNodesFromConfigurationData(self, serialized: Dict[str, Any]) -> None:
        for key, data in serialized.items():
            self.registerNode(NodeFactory.createNode(key, data))

    def _registerConnectionsFromConfigurationData(self, serialized: List[Dict[str, str]]) -> None:
        for connection_dict in serialized:
            self._nodes[connection_dict["from"]].connectWith(connection_dict["resource_type"],
                                                             self._nodes[connection_dict["to"]])

    def getAllNodeIds(self) -> List[str]:
        return [node.getId() for node in self._nodes.values()]

    def _preUpdate(self) -> None:
        self.preUpdateCalled.emit()
        for node in self._nodes.values():
            if node.enabled:
                node.preUpdate()

    def _updateReservations(self) -> None:
        """
        The update reservations step is the moment where all nodes request an initial amount of resources.
        These resources will be divided equally (If a provider can offer 8 "energy" and two consumers ask for 8, each
        of these will get 4). This can mean that they won't get enough to function.

        Potential relaxation of these reservations will be done in _replanReservations.
        """
        for node in self._nodes.values():
            if node.enabled:
                node.updateReservations()

    def _replanReservations(self) -> None:
        """
        This is the follow up to _updateReservations. Once a single reservation is made, it can be that certain changes
        must be made to the planning.

        Example:
        Battery_1 (8 Power), Battery_2 (6 power), Battery_3 (8 power), Light_1 (requires 8 power) and Light_2 (req 8)
        Battery_1 is connected with Light_1, battery_2 is connected with both lights, battery_3 is connected to light_2.
        In the initial _update reservation, Light_1 will get 4 power from battery_1, 3 from battery_2 (requested 4,
        but due to light 2 only got 3). Light_2 will get 3 power from battery_2 and 4 power from battery 3.
        Neither of the lights will go on (as both of them only got 7!).
        The _replanReservation will attempt to relax the original reservation a bit. By asking 1 power more of batter_1
        and battery_3, the requests can be resolved.
        """
        while True:
            run_again = False
            for node in self._nodes.values():
                if not node.enabled:
                    continue
                if node.requiresReplanning():
                    run_again = True
                    node.replanReservations()
            if not run_again:
                break
            self._updateReservations()

    def _update(self) -> None:
        self.updateCalled.emit()
        sub_tick_modifier = 1 / self._sub_ticks
        for _ in range(0, self._sub_ticks):
            for node in self._nodes.values():
                if node.enabled:
                    node.update(sub_tick_modifier)
            print("SUBTICK END")
        for node in self._nodes.values():
            node.updateModifiers()

    def _postUpdate(self) -> None:
        self.postUpdateCalled.emit()
        for node in self._nodes.values():
            if node.enabled:
                node.postUpdate()

    def doTick(self) -> None:
        """
        Handle a single tick.
        """
        print("TICK STARTED", self._tick_count + 1)
        with self._update_lock:
            self._updateOutsideTemperature()
            self._preUpdate()
            self._updateReservations()
            self._replanReservations()
            self._update()
            self._postUpdate()
            self._tick_count += 1
            self.tickCompleted.emit()
        print("TICK ENDED!")

    def _getResourceColor(self, resource_type: str) -> str:
        if resource_type == "energy":
            return "yellow"
        if resource_type == "water":
            return "blue"
        if resource_type == "plants":
            return "green"
        return ""

    def generatePlantUMLGraph(self) -> str:
        result = "@startuml\nskinparam linetype ortho\n"

        for node_id in self._nodes:
            result += "map {node_id}".format(node_id = node_id)
            result += "{\n"
            result += "    Weight => {weight}\n".format(weight = self._nodes[node_id].weight)
            result += "    Max temp => {max_safe_temperature}\n".format(max_safe_temperature=self._nodes[node_id].max_safe_temperature)
            result += "}\n"

        for node in self._nodes.values():
            for connection in node.getAllOutgoingConnections():
                color = self._getResourceColor(connection.resource_type)
                color_string = "[#{color}]".format(color = color) if color else ""
                result += "{origin} -{color}-> {target}\n".format(origin = connection.origin.getId(),
                                                                  target = connection.target.getId(),
                                                                  color = color_string)

        result += "@enduml"

        return result