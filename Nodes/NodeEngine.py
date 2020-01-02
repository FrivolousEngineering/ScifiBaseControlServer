from typing import List, Dict, Any

from Nodes.Node import Node
from Nodes.NodeFactory import NodeFactory

from atomicwrites import atomic_write

import json


class NodeEngine:
    """
    The node engine is responsible for handling ticks (a single update) and subsequently ensuring that all nodes in it's
    list get updated. Once this tick is completed, the state is left in such a way that data can be read (eg; What
    nodes got what they wanted, which didn't, etc).
    """
    def __init__(self) -> None:
        self._nodes = {}  # type: Dict[str, Node]
        pass

    def registerNode(self, node: Node) -> None:
        if node.getId() not in self._nodes:
            self._nodes[node.getId()] = node
        else:
            raise KeyError("Node must have an unique ID!")

    def registerNodesFromConfigurationData(self, serialized: Dict[str, Any]) -> None:
        for key, data in serialized.items():
            self.registerNode(NodeFactory.createNode(key, data))

    def registerConnectionsFromConfigurationData(self, serialized: List[Dict[str, str]]) -> None:
        for connection_dict in serialized:
            self._nodes[connection_dict["from"]].connectWith(connection_dict["resource_type"],
                                                             self._nodes[connection_dict["to"]])

    def storeNodeStateToFile(self):
        data_to_write = []
        for node in self._nodes.values():
            data_to_write.append(node.serialize())

        with atomic_write("node_state.json", overwrite = True) as f:
            # TODO: This always overrides, which isn't that safe. Might want to think about a somewhat smarter solution
            # that keeps a number of previous states (so if one fails it can still recover an older one)
            f.write(json.dumps(data_to_write, separators = (", ", ": "), indent = 4))

    def restoreNodeStateFromFile(self):
        with open("node_state.json") as f:
            data = f.read()

        parsed_json = json.loads(data)
        for entry in parsed_json:
            #TODO: This has no fault handling what so ever, which should be added at some point.
            node = self._nodes[entry["node_id"]]
            node.deserialize(entry)

    def getAllNodeIds(self) -> List[str]:
        return [node.getId() for node in self._nodes.values()]

    def _preUpdate(self) -> None:
        for node in self._nodes.values():
            node.preUpdate()

    def _updateReservations(self) -> None:
        """
        The update reservations step is the moment where all nodes request an initial amount of resources.
        These resources will be divided equally (If a provider can offer 8 "energy" and two consumers ask for 8, each
        of these will get 4). This can mean that they won't get enough to function.

        Potential relaxation of these reservations will be done in _replanReservations.
        """
        for node in self._nodes.values():
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
                if node.requiresReplanning():
                    run_again = True
                    node.replanReservations()
            if not run_again:
                break
            self._updateReservations()

    def _update(self) -> None:
        for node in self._nodes.values():
            node.update()

    def _postUpdate(self) -> None:
        for node in self._nodes.values():
            node.postUpdate()

    def doTick(self) -> None:
        """
        Handle a single tick.
        """
        print("TICK STARTED")
        self._preUpdate()
        self._updateReservations()
        self._replanReservations()
        self._update()
        self._postUpdate()
        print("TICK ENDED!")
