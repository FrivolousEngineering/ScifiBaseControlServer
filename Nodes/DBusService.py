
import dbus
import dbus.service
from typing import List
from Nodes.NodeEngine import NodeEngine


class DBusService(dbus.service.Object):
    def __init__(self, engine: NodeEngine) -> None:
        self._bus = dbus.SessionBus()
        super().__init__(
            bus_name = dbus.service.BusName("com.frivengi.nodes", self._bus),
            object_path = "/com/frivengi/nodes"
        )

        self._node_engine = engine

    @dbus.service.method("com.frivengi.nodes", out_signature="s", in_signature = "s")
    def getNodeInfo(self, node_id: str) -> str:
        return str(self._node_engine.getNodeById(node_id))

    @dbus.service.method("com.frivengi.nodes", out_signature="d", in_signature="s")
    def getNodeTemperature(self, node_id: str) -> float:
        node = self._node_engine.getNodeById(node_id)
        if node:
            return node.temperature
        return -9000.

    @dbus.service.method("com.frivengi.nodes", out_signature="ad", in_signature="s")
    def getNodeTemperatureHistory(self, node_id: str) -> List[float]:
        history = self._node_engine.getNodeHistoryById(node_id)
        if history:
            return history.getTemperatureHistory()
        return []

    @dbus.service.method("com.frivengi.nodes")
    def doTick(self) -> None:
        self._node_engine.doTick()