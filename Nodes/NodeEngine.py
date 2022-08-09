from threading import RLock
from typing import List, Dict, Any, Optional

from Nodes.Node import Node
from Nodes.NodeFactory import NodeFactory
from Nodes.NodeHistory import NodeHistory
from Nodes.TemperatureHandlers.TemperatureHandler import TemperatureHandler
from Nodes.PerpetualTimer import PerpetualTimer
from Signal import signalemitter, Signal
import random
TICK_INTERVAL = 120  # Seconds


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
        """
        Create a node Engine which controls a set of Nodes.
        """
        self._nodes: Dict[str, Node] = {}
        self._node_histories: Dict[str, NodeHistory] = {}

        self._update_lock = RLock()

        self._tick_timer = PerpetualTimer(TICK_INTERVAL, self.doTick)

        self._outside_temperature_handler: Optional[TemperatureHandler] = None
        self._tick_count: int = 0

        self._sub_ticks: int = 10
        """
        How many "in between" updates per tick should be done? This should be seen as "micro" ticks. Instead of doing
        the update of a tick in one go, it will be cut up in smaller chunks (so with 30 sub ticks, there will be 30
        calls to update, but in each of these only 1/30th of the production is done.
        We also randomise the order of the nodes in between these steps (although we use a seed for this to make it
        deterministic. The randomisation ensures that the order in which the update of each node is done is much less
        of a factor. If you see weird fluctuating behavior, increase the amount of sub-ticks. Do note that this does
        mean that more calculations are done, which might negatively impact larger systems.
        """

        self._default_outside_temperature = 293.15

    def resetSeed(self) -> None:
        """
        When using 'sub-tick updates' we randomize the order in which we handle the updates
        """
        random.seed(self._tick_count)

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def setOutsideTemperatureHandler(self, temp_handler: TemperatureHandler) -> None:
        """
        Set a handler that controls the outside temperature (which can vary over time)
        :param temp_handler:
        :return:
        """
        self._outside_temperature_handler = temp_handler

    def _updateOutsideTemperature(self) -> None:
        """
        Update the ambient temperature by using the outside temp handler (if any)
        :return:
        """
        new_temperature = self._default_outside_temperature
        if self._outside_temperature_handler is not None:
            new_temperature = self._outside_temperature_handler.getTemperatureForTick(self._tick_count)

        for node in self.getAllNodes().values():
            node.outside_temp = new_temperature

    def start(self) -> None:
        """
        Start the automatic run of the node engine (do a tick per time passed)
        """
        self._tick_timer.start()

    def stop(self) -> None:
        """
        Stop the automatic run of the node engine (do a tick per time passed)
        """
        self._tick_timer.cancel()

    @property
    def paused(self):
        return not self._tick_timer.is_running

    def registerNode(self, node: Node) -> None:
        """
        Add a node to be tracked / updated by the node engine.
        :param node: the node to be added.
        """
        if node.getId() not in self._nodes:
            self._nodes[node.getId()] = node
            self.preUpdateCalled.connect(node.acquireUpdateLock)
            self.postUpdateCalled.connect(node.releaseUpdateLock)
            self._node_histories[node.getId()] = NodeHistory(node)
            node.ensureSaneValues()
        else:
            raise KeyError("Node must have an unique ID!")

    def getAllNodes(self) -> Dict[str, Node]:
        """
        Get all nodes known by the engine.

        TODO: It might not be the smartest move to return this by reference.
        :return: The nodes in a dict with their Id's as keys
        """
        return self._nodes

    def getNodeById(self, node_id: str) -> Optional[Node]:
        """
        Get a specific node by providing it's id
        :param node_id: ID of the node
        :return: The node (if found)
        """
        return self._nodes.get(node_id)

    def getNodeHistoryById(self, node_id: str) -> Optional[NodeHistory]:
        """
        Get the history object of a specific node
        :param node_id: The ID of the node
        :return: The history (if any)
        """
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
        """
        The NodeEngine can be filled by config data. This function makes sure that the nodes are created
        :param serialized: Dict that describes the nodes to be created
        """
        for key, data in serialized.items():
            self.registerNode(NodeFactory.createNode(key, data))

    def _registerConnectionsFromConfigurationData(self, serialized: List[Dict[str, str]]) -> None:
        """
        The NodeEngine can be filled by config data. This function makes sure that the connections are created.

        This function *MUST* be called after :py:meth:Nodes.nodeEngine.NodeEngine._registerNodesFromConfigurationData
        since it needs nodes to actually create the connections
        :param serialized: Dict that describes the connections to be created
        """
        for connection_dict in serialized:
            if connection_dict["from"] not in self._nodes:
                raise KeyError(f"Could not find node with id {connection_dict['from']} to connect from")
            if connection_dict["to"] not in self._nodes:
                raise KeyError(f"Could not find node with id '{connection_dict['to']}' to connect to")
            self._nodes[connection_dict["from"]].connectWith(connection_dict["resource_type"],
                                                             self._nodes[connection_dict["to"]])

    def getAllNodeIds(self) -> List[str]:
        """
        Get a list of all Node ID's
        :return: The list (much suprise!)
        """
        return [node.getId() for node in self._nodes.values()]

    def _preUpdate(self) -> None:
        """
        Handle the pre-update of the Node engine.
        This basically calls the pre-update for all nodes.
        """
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
        """
        Handle the actual update.
        """
        self.updateCalled.emit()
        sub_tick_modifier = 1 / self._sub_ticks
        for i in range(0, self._sub_ticks):
            keys = list(self._nodes.keys())
            # Yeah. Randomness. I know. But combined with the sub ticks, it's the only way to make sure that the order
            # in which the nodes are updated is no longer a factor. To at least make its reproducible, we use the tick
            # count as the seed for the randomness.
            random.shuffle(keys)
            for node_id in keys:
                node = self._nodes[node_id]
                if node.enabled:
                    node.update(sub_tick_modifier)
                node.cleanupAfterUpdate()
            #print("SUBTICK END")
        for node in self._nodes.values():
            node.updateModifiers()

    def _postUpdate(self) -> None:
        """
        Handle everything that needs to be done after all the updating has been done.
        For more info what happens during the post update, check the Node documentation.
        :return:
        """
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

        self.resetSeed()
        print("TICK ENDED!")
